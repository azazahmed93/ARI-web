"""
Activation tab — mapping preview and audience creation UI.

Phase A: Shows how ARI segments map to taxonomy segments (Generic or Epsilon)
         across demographics, interests, psychographics, and attitudes.
Phase B: Creates and activates audiences via the OpenX GraphQL API (Generic only).
"""

import streamlit as st
from core.openx_service import OpenXService
from core.openx_mapper import (
    preview_all_segments as openx_preview_all_segments,
    build_audience_params,
    build_deal_params,
    resolve_segment_ids,
    load_taxonomy,
    TAXONOMY_CSV_PATH,
)
from core.epsilon_mapper import (
    preview_all_segments as epsilon_preview_all_segments,
    load_epsilon_taxonomy,
    EPSILON_CSV_PATH,
)


def _confidence_badge(confidence: float) -> str:
    """Return an HTML badge colored by confidence level."""
    if confidence >= 0.80:
        color, label = "#10b981", "High"
    elif confidence >= 0.50:
        color, label = "#f59e0b", "Medium"
    else:
        color, label = "#ef4444", "Low"
    return (
        f'<span style="background:{color};color:#fff;padding:2px 8px;'
        f'border-radius:12px;font-size:0.75rem;font-weight:600;">'
        f'{label} ({confidence:.0%})</span>'
    )


def _render_match_section(title: str, matches: list):
    """Render a list of matched segments with confidence badges."""
    if not matches:
        st.markdown(f"**{title}**: _No matches_")
        return
    for m in matches:
        seg = m.get("segment", {})
        name = seg.get("name", "Unknown")
        full_name = seg.get("full_name", "")
        conf = m.get("confidence", 0)
        note = m.get("note", "")

        display = full_name if full_name else name
        badge = _confidence_badge(conf)
        extra = f' <span style="color:#6b7280;font-size:0.8rem;">({note})</span>' if note else ""
        st.markdown(
            f"&nbsp;&nbsp;&nbsp;&nbsp;{display} {badge}{extra}",
            unsafe_allow_html=True,
        )


def _render_trait_matches(title: str, matches: list):
    """Render trait-based matches (activities, routines, mosaic, attitudes)."""
    if not matches:
        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;_No matches_")
        return
    for m in matches:
        seg = m.get("segment", {})
        display = seg.get("full_name", seg.get("name", "Unknown"))
        conf = m.get("confidence", 0)
        source = m.get("source_trait", "")
        badge = _confidence_badge(conf)
        source_label = (
            f' <span style="color:#6b7280;font-size:0.75rem;">'
            f'from "{source}"</span>'
            if source else ""
        )
        st.markdown(
            f"&nbsp;&nbsp;&nbsp;&nbsp;{display} {badge}{source_label}",
            unsafe_allow_html=True,
        )


def _build_epsilon_csv_export(
    previews: list, selected_indices: list, custom_picks: dict
) -> str:
    """Build a CSV string of all matched Epsilon segments across selected ARI segments."""
    import io
    import csv as _csv

    buf = io.StringIO()
    writer = _csv.writer(buf)
    writer.writerow([
        "ARI Segment Label",
        "ARI Segment Name",
        "Match Category",
        "Dimension",
        "Sub-Category",
        "Epsilon Attribute",
        "Value",
        "Value Definition",
        "Field Name",
        "DE Rate ID",
        "Confidence",
        "Source",
    ])

    def _row(label, seg_name, match_cat, seg_dict, confidence, source):
        writer.writerow([
            label,
            seg_name,
            match_cat,
            seg_dict.get("category", ""),
            seg_dict.get("sub_category", ""),
            seg_dict.get("epsilon_name", ""),
            seg_dict.get("epsilon_value", ""),
            seg_dict.get("epsilon_value_definition", seg_dict.get("name", "")),
            seg_dict.get("epsilon_field_name", ""),
            seg_dict.get("epsilon_de_rate_id", ""),
            f"{confidence:.2f}" if isinstance(confidence, (int, float)) else "",
            source,
        ])

    for idx in selected_indices:
        preview = previews[idx]
        label = preview.get("label", f"Segment {idx + 1}")
        seg_name = preview.get("segment_name", "")
        matches = preview.get("matches", {})

        # AI matches
        for cat, items in matches.items():
            if not isinstance(items, list):
                continue
            for m in items:
                if not isinstance(m, dict):
                    continue
                seg = m.get("segment") or {}
                if not seg:
                    continue
                conf = m.get("confidence", 0)
                _row(label, seg_name, cat, seg, conf, "AI")

        # Custom picks (use AI-ranked confidence if available)
        for seg in custom_picks.get(idx, []):
            conf = seg.get("ai_confidence", 1.0)
            _row(label, seg_name, "custom", seg, conf, "Custom")

    return buf.getvalue()


def _search_taxonomy(query: str, taxonomy: list, limit: int = 20) -> list:
    """Case-insensitive substring search over taxonomy rows.

    For Epsilon rows, skips non-targetable values (No/Blank/Unknown).
    """
    if not query or not taxonomy:
        return []
    q = query.lower().strip()
    if len(q) < 2:
        return []
    skip_values = {"no", "blank", "unknown", "absent", "not available"}
    results = []
    for row in taxonomy:
        # Skip Epsilon negative/unknown flag rows
        eps_val = (row.get("epsilon_value") or "").lower()
        if eps_val in skip_values:
            continue
        name_lower = row.get("name", "").lower()
        if name_lower in skip_values:
            continue

        full_name = row.get("full_name", "")
        if q in name_lower or q in full_name.lower():
            results.append(row)
            if len(results) >= limit:
                break
    return results


def _collect_ai_matched_full_names(matches: dict) -> set:
    """Collect full_names of all segments already matched by the AI."""
    seen = set()
    for val in matches.values():
        if not isinstance(val, list):
            continue
        for m in val:
            if not isinstance(m, dict):
                continue
            seg = m.get("segment", {}) or {}
            fn = seg.get("full_name", "")
            if fn:
                seen.add(fn)
            # Handle age match entries with all_segments_in_range
            for inner in m.get("all_segments_in_range", []) or []:
                inner_fn = inner.get("full_name", "")
                if inner_fn:
                    seen.add(inner_fn)
    return seen


def _render_custom_picks_section(
    source_key: str,
    ari_idx: int,
    taxonomy: list,
    matches: dict,
    is_epsilon: bool,
    ari_segment: dict = None,
    audience_insights: dict = None,
):
    """Render the 'Add More Segments' search + picks UI for one ARI segment."""
    state_key = f"custom_picks_{source_key}"
    picks_by_idx = st.session_state.get(state_key, {})
    current_picks = picks_by_idx.get(ari_idx, [])
    picked_fns = {p.get("full_name", "") for p in current_picks}
    ai_matched_fns = _collect_ai_matched_full_names(matches)

    label = "PRIZM Clusters" if is_epsilon else "Taxonomy Segments"
    st.markdown(f"##### Add More {label}")
    st.caption(
        "Search the taxonomy to add segments the AI may have missed."
        + ("" if not is_epsilon else " (Preview only for Epsilon)")
    )

    search_key = f"search_{source_key}_{ari_idx}"
    query = st.text_input(
        "Search",
        key=search_key,
        placeholder="Type to search segment name...",
        label_visibility="collapsed",
    )

    def _render_row(seg: dict, context: str, row_idx: int):
        """Render a single segment row with Add/Remove + optional AI confidence."""
        fn = seg.get("full_name", "")
        is_picked = fn in picked_fns
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            display = fn or seg.get("name", "?")
            conf = seg.get("ai_confidence")
            badge_html = ""
            if is_picked and conf is not None:
                badge_html = f" {_confidence_badge(conf)}"
            st.markdown(
                f"<span style='font-size:0.88rem'>{display}</span>{badge_html}",
                unsafe_allow_html=True,
            )
            if context == "added" and is_picked and seg.get("ai_reasoning"):
                st.caption(f"{seg['ai_reasoning']}")
        with col2:
            btn_label = "Remove" if is_picked else "Add"
            # Include value + field_name + positional index to guarantee uniqueness
            disambig = f"{seg.get('epsilon_value','')}_{seg.get('epsilon_field_name','')}_{row_idx}"
            btn_key = f"{context}_{source_key}_{ari_idx}_{hash(fn)}_{hash(disambig)}"
            if st.button(btn_label, key=btn_key):
                if is_picked:
                    picks_by_idx[ari_idx] = [
                        p for p in current_picks
                        if p.get("full_name") != fn
                    ]
                else:
                    picks_by_idx.setdefault(ari_idx, []).append(seg)
                st.session_state[state_key] = picks_by_idx
                st.rerun()

    if query:
        raw_results = _search_taxonomy(query, taxonomy, limit=50)
        # Drop segments already matched by the AI
        results = [s for s in raw_results if s.get("full_name", "") not in ai_matched_fns][:15]

        if not results:
            st.caption("_No new matches found._")
        else:
            st.caption(f"Showing {len(results)} match(es):")
            for i, seg in enumerate(results):
                _render_row(seg, context="search", row_idx=i)

    # Always show all currently added picks at the end
    if current_picks:
        col_left, col_right = st.columns([0.7, 0.3])
        with col_left:
            st.markdown("**Added segments:**")
        with col_right:
            if ari_segment is not None and st.button(
                "Rank with AI",
                key=f"rank_{source_key}_{ari_idx}",
                use_container_width=True,
            ):
                with st.spinner("Scoring relevance..."):
                    from core.ai_ranking import rank_custom_picks
                    rankings = rank_custom_picks(
                        ari_segment,
                        audience_insights or {},
                        current_picks,
                    )
                if rankings:
                    for seg in current_picks:
                        fn = seg.get("full_name", "")
                        if fn in rankings:
                            seg["ai_confidence"] = rankings[fn]["confidence"]
                            seg["ai_reasoning"] = rankings[fn]["reasoning"]
                    picks_by_idx[ari_idx] = current_picks
                    st.session_state[state_key] = picks_by_idx
                    st.rerun()
                else:
                    st.error("AI ranking failed. Please try again.")

        for i, seg in enumerate(current_picks):
            _render_row(seg, context="added", row_idx=i)


def render_openx_activation():
    """Main entry point — called from the results tab."""

    # ---------- Taxonomy source toggle ----------
    source = st.radio(
        "Taxonomy",
        ["Generic", "Epsilon"],
        horizontal=True,
        key="activation_taxonomy_source",
    )
    is_epsilon = source == "Epsilon"

    # ---------- Taxonomy check ----------
    if is_epsilon:
        taxonomy = load_epsilon_taxonomy()
        csv_path = EPSILON_CSV_PATH
        cache_key = "epsilon_mapping_preview"
        preview_fn = epsilon_preview_all_segments
    else:
        taxonomy = load_taxonomy()
        csv_path = TAXONOMY_CSV_PATH
        cache_key = "openx_mapping_preview"
        preview_fn = openx_preview_all_segments

    if not taxonomy:
        st.info(
            f"**Segment Taxonomy** not found.\n\n"
            f"Place the taxonomy CSV at `{csv_path}`."
        )
        return

    # ---------- API config check (Generic only) ----------
    api_configured = False
    if not is_epsilon:
        api_configured = OpenXService.is_configured()
        if not api_configured:
            st.caption(
                "API not configured — mapping preview is available, "
                "but audience creation requires API credentials."
            )

    # ---------- Phase A: Mapping Preview ----------
    st.subheader("Audience Mapping Preview")
    st.caption(
        "Review how ARI audience segments map to taxonomy segments. "
        + ("Select the segments you want to activate." if not is_epsilon else "")
    )

    # Generate previews (once per source)
    if st.session_state.get(cache_key) is None:
        with st.spinner("Matching ARI segments to taxonomy..."):
            previews = preview_fn(dict(st.session_state))
            st.session_state[cache_key] = previews

    previews = st.session_state[cache_key] or []

    if not previews:
        st.warning("No audience segments found. Please run an analysis first.")
        return

    # Selection checkboxes
    selected = {}
    for preview in previews:
        label = preview["label"]
        seg_name = preview["segment_name"]
        idx = preview["index"]
        summary = preview["summary"]
        warnings = preview["warnings"]

        prefix = "eps" if is_epsilon else "openx"
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            selected[idx] = st.checkbox("", value=True, key=f"{prefix}_sel_{idx}")
        with col2:
            with st.expander(f"**{label}**: {seg_name}", expanded=False):
                # --- Summary row ---
                _render_summary_row(summary)

                matches = preview["matches"]

                # --- 1. Core Demographics ---
                st.markdown("##### Core Demographics")

                # Age
                st.markdown("**Age Segments**")
                age_matches = matches.get("age", [])
                if age_matches:
                    names = [r["segment"]["name"] for r in age_matches if r.get("segment")]
                    if len(names) >= 2:
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;&nbsp;Age range: {names[0]} - {names[-1]} "
                            f"{_confidence_badge(1.0)}",
                            unsafe_allow_html=True,
                        )
                    else:
                        _render_match_section("Age", age_matches)
                else:
                    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;_No matches_")

                # Gender
                st.markdown("**Gender**")
                _render_match_section("Gender", matches.get("gender", []))

                # --- 2. Location (Generic only) ---
                if not is_epsilon:
                    st.markdown("##### Location")

                    st.markdown("**State**")
                    _render_match_section("State", matches.get("location", []))

                    st.markdown("**Area Type**")
                    area_matches = matches.get("area_type", [])
                    if area_matches:
                        _render_match_section("Area Type", area_matches)
                    else:
                        st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;_No matches_")

                # --- 3. Advanced Demographics ---
                st.markdown("##### Advanced Demographics")

                st.markdown("**Income**")
                income_matches = matches.get("income", [])
                if income_matches:
                    _render_match_section("Income", income_matches)
                else:
                    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;_No matches_")

                st.markdown("**Education**")
                education_matches = matches.get("education", [])
                if education_matches:
                    _render_match_section("Education", education_matches)
                else:
                    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;_No matches_")

                st.markdown("**Marital Status**")
                marital_matches = matches.get("marital", [])
                if marital_matches:
                    _render_match_section("Marital", marital_matches)
                else:
                    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;_No matches_")

                st.markdown("**Children**")
                children_matches = matches.get("children", [])
                if children_matches:
                    _render_match_section("Children", children_matches)
                else:
                    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;_No matches_")

                # --- 4. Language (Generic only) ---
                if not is_epsilon:
                    st.markdown("##### Language")
                    language_matches = matches.get("language", [])
                    if language_matches:
                        _render_match_section("Language", language_matches)
                    else:
                        st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;_No matches_")

                # --- 5. Interests & Activities ---
                st.markdown("##### Interests & Activities")

                st.markdown("**Interest Categories**")
                interest_matches = matches.get("interests", [])
                for im in interest_matches:
                    seg = im.get("segment", {})
                    seg_display = seg.get("full_name", seg.get("name", "—"))
                    conf = im.get("confidence", 0)
                    if im.get("matched"):
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;&nbsp;{im['input']} &rarr; "
                            f"{seg_display} {_confidence_badge(conf)}",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;&nbsp;{im['input']} &rarr; "
                            f'<span style="color:#ef4444;font-size:0.85rem;">No match</span>',
                            unsafe_allow_html=True,
                        )

                st.markdown("**Activities** _(from psychographic profile)_")
                _render_trait_matches("Activities", matches.get("activities", []))

                st.markdown("**Daily Routines** _(from psychographic profile)_")
                _render_trait_matches("Daily Routines", matches.get("daily_routines", []))

                # --- 6. Psychographic ---
                st.markdown("##### Psychographic")

                persona_label = "PRIZM Clusters" if is_epsilon else "Mosaic Persona"
                st.markdown(f"**{persona_label}**")
                _render_trait_matches(persona_label, matches.get("mosaic_persona", []))

                if not is_epsilon:
                    st.markdown("**Attitudes** _(Tech Adoption, Health, Mobile Usage)_")
                    _render_trait_matches("Attitudes", matches.get("attitudes", []))

                # --- 7. Taxonomy ---
                st.markdown("##### Taxonomy (Industry)")
                taxonomy_matches = matches.get("taxonomy", [])
                if taxonomy_matches:
                    for tm in taxonomy_matches[:5]:
                        seg = tm.get("segment", {})
                        display = seg.get("full_name", seg.get("name", "Unknown"))
                        conf = tm.get("confidence", 0)
                        cat = seg.get("category", "")
                        cat_label = (
                            f' <span style="color:#6b7280;font-size:0.75rem;">[{cat}]</span>'
                            if cat else ""
                        )
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;&nbsp;{display}{cat_label} "
                            f"{_confidence_badge(conf)}",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;_No taxonomy matches_")

                # --- 8. Ethnic Affinity Keywords ---
                ethnic_kw = matches.get("ethnic_keywords", {})
                ethnic_words = ethnic_kw.get("keywords", [])
                ethnicity = ethnic_kw.get("ethnicity")
                kw_sources = ethnic_kw.get("sources", [])

                st.markdown("##### Contextual Keywords (Ethnic Affinity)")
                if ethnic_words:
                    kw_display = ", ".join(ethnic_words)
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{kw_display}")
                    if ethnicity:
                        st.caption(f"Detected ethnicity: {ethnicity}")
                else:
                    st.markdown(
                        "&nbsp;&nbsp;&nbsp;&nbsp;_No ethnic affinity detected — "
                        "general market segment_"
                    )

                # --- 9. Epsilon-exclusive sections ---
                if is_epsilon:
                    auto_matches = matches.get("automotive", [])
                    if auto_matches:
                        st.markdown("##### Automotive")
                        _render_trait_matches("Automotive", auto_matches)

                    health_matches = matches.get("health", [])
                    if health_matches:
                        st.markdown("##### Health")
                        _render_trait_matches("Health", health_matches)

                    trigger_matches = matches.get("trigger_events", [])
                    if trigger_matches:
                        st.markdown("##### Life Events (Triggers)")
                        _render_trait_matches("Triggers", trigger_matches)

                # --- 10. Custom segment picker (search + add) ---
                st.markdown("---")
                # Grab audience_insights from session state for AI ranking context
                _ai_insights = st.session_state.get("audience_insights", {})
                if isinstance(_ai_insights, str):
                    import json as _json
                    try:
                        _ai_insights = _json.loads(_ai_insights)
                    except Exception:
                        _ai_insights = {}
                _render_custom_picks_section(
                    source_key="epsilon" if is_epsilon else "openx",
                    ari_idx=idx,
                    taxonomy=taxonomy,
                    matches=matches,
                    is_epsilon=is_epsilon,
                    ari_segment=preview.get("segment_data", {}),
                    audience_insights=_ai_insights,
                )

                # Warnings
                if warnings:
                    for w in warnings:
                        st.warning(w, icon="⚠️")

    # ---------- Phase B: Audience Creation ----------
    st.markdown("---")

    if is_epsilon:
        selected_indices = [idx for idx, sel in selected.items() if sel]
        custom_picks = st.session_state.get("custom_picks_epsilon", {})

        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.info("Preview only — audience creation is available for Generic taxonomy.")
        with col2:
            if selected_indices:
                csv_content = _build_epsilon_csv_export(
                    previews, selected_indices, custom_picks
                )
                from datetime import datetime
                filename = f"epsilon_segments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                st.download_button(
                    label="Export as CSV",
                    data=csv_content,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.caption("Select at least one segment to enable export.")
        return

    selected_indices = [idx for idx, sel in selected.items() if sel]

    if st.session_state.get("openx_creation_complete"):
        _render_creation_results()
        return

    if not api_configured:
        st.info(
            "API credentials not configured. "
            "Contact your administrator to enable audience creation."
        )
        return

    # Connectivity check (once per session)
    service = OpenXService()
    if "openx_ping_ok" not in st.session_state:
        st.session_state.openx_ping_ok = service.ping()

    if not st.session_state.openx_ping_ok:
        st.error("Could not connect to the activation API. Verify your API key and URL.")
        if st.button("Retry Connection"):
            st.session_state.openx_ping_ok = service.ping()
            st.rerun()
        return

    create_btn = st.button(
        f"Create {len(selected_indices)} Selected Audience(s)",
        type="primary",
        disabled=len(selected_indices) == 0,
    )

    if create_btn and selected_indices:
        _create_audiences(service, previews, selected_indices)


def _render_summary_row(summary: dict):
    """Render the compact summary counts for a segment preview."""
    # Core counts
    parts = [
        f"Age: **{summary.get('age_matches', 0)}**",
        f"Gender: **{summary.get('gender_matches', 0)}**",
        f"Location: **{summary.get('location_matches', 0)}**",
        f"Interests: **{summary.get('interest_matches', 0)}/{summary.get('interest_total', 0)}**",
        f"Taxonomy: **{summary.get('taxonomy_matches', 0)}**",
    ]

    # New category counts (only show if > 0)
    new_counts = {
        "Income": summary.get("income_matches", 0),
        "Education": summary.get("education_matches", 0),
        "Language": summary.get("language_matches", 0),
        "Area": summary.get("area_matches", 0),
        "Children": summary.get("children_matches", 0),
        "Marital": summary.get("marital_matches", 0),
        "Activities": summary.get("activities_matches", 0),
        "Routines": summary.get("routines_matches", 0),
        "Mosaic": summary.get("mosaic_matches", 0),
        "Attitudes": summary.get("attitude_matches", 0),
        "Keywords": summary.get("ethnic_keyword_count", 0),
        "Automotive": summary.get("automotive_matches", 0),
        "Health": summary.get("health_matches", 0),
        "Triggers": summary.get("trigger_matches", 0),
    }
    for label, count in new_counts.items():
        if count > 0:
            parts.append(f"{label}: **{count}**")

    st.markdown(" &nbsp;|&nbsp; ".join(parts))


def _create_audiences(
    service: OpenXService, previews: list, selected_indices: list
):
    """Create and activate audiences for selected segments."""
    created = []
    progress = st.progress(0, text="Resolving segment IDs...")

    # Merge any user-added custom picks into each preview's matches under "custom"
    custom_picks = st.session_state.get("custom_picks_openx", {})
    for idx in selected_indices:
        picks = custom_picks.get(idx, [])
        if picks:
            previews[idx]["matches"]["custom"] = [
                {"segment": seg, "confidence": seg.get("ai_confidence", 1.0)}
                for seg in picks
            ]

    # Resolve all segment IDs upfront (one API batch per category)
    all_matches = {}
    for idx in selected_indices:
        for key, val in previews[idx]["matches"].items():
            if not isinstance(val, list):
                continue  # skip non-list entries like ethnic_keywords
            all_matches.setdefault(key, []).extend(val)
    id_map = resolve_segment_ids(all_matches, service)

    for i, idx in enumerate(selected_indices):
        preview = previews[idx]
        seg = preview["segment_data"]
        matches = preview["matches"]

        progress.progress(
            (i / len(selected_indices)),
            text=f"Creating: {preview['segment_name']}...",
        )

        params = build_audience_params(seg, matches, id_map)
        result = service.create_audience(params)

        if result:
            audience_id = result.get("id", "")
            audience_name = result.get("name", params["name"])
            activated = service.activate_audience(audience_id) if audience_id else False

            # Auto-create deal after activation
            deal_result = None
            if activated and audience_id:
                ethnic_kw = matches.get("ethnic_keywords", {})
                deal_params = build_deal_params(
                    audience_id, audience_name,
                    ethnic_keywords=ethnic_kw.get("keywords") or None,
                )
                from core.openx_mapper import OPENX_DEAL_ID_PREFIX
                deal_result = service.create_deal(deal_params, deal_id_prefix=OPENX_DEAL_ID_PREFIX)

            entry = {
                "id": audience_id,
                "name": audience_name,
                "segment_label": preview["label"],
                "segment_name": preview["segment_name"],
            }
            if deal_result:
                entry["status"] = "Activated + Deal created"
                entry["deal_id"] = deal_result.get("deal_id", "")
                entry["deal_name"] = deal_result.get("name", "")
                entry["deal_uuid"] = deal_result.get("id", "")
            elif activated:
                entry["status"] = "Activating (~6-10 hours) — deal creation failed"
            else:
                entry["status"] = "Created (activation failed)"
            created.append(entry)
        else:
            created.append({
                "id": None,
                "name": params["name"],
                "status": "Creation failed",
                "segment_label": preview["label"],
                "segment_name": preview["segment_name"],
            })

    progress.progress(1.0, text="Done!")
    st.session_state.openx_audiences = created
    st.session_state.openx_creation_complete = True
    st.rerun()


def _render_creation_results():
    """Display audience creation results with copyable IDs."""
    st.subheader("Audience Creation Results")

    audiences = st.session_state.get("openx_audiences", [])
    if not audiences:
        st.info("No audiences created yet.")
        return

    deals = [a for a in audiences if a.get("deal_id")]
    failed = [a for a in audiences if not a.get("id")]

    if deals:
        deal_text = "\n".join(
            f"{a['segment_label']}: {a['deal_id']}"
            for a in deals
        )
        st.code(deal_text, language=None)
    if failed:
        st.error(f"{len(failed)} audience(s) failed to create.")

    if st.button("Reset & Create New Audiences"):
        st.session_state.openx_mapping_preview = None
        st.session_state.openx_audiences = []
        st.session_state.openx_creation_complete = False
        st.session_state.custom_picks_openx = {}
        st.rerun()
