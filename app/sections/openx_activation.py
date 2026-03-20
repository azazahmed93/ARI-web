"""
OpenX Activation tab — mapping preview and audience creation UI.

Phase A: Shows how ARI segments map to OpenXSelect taxonomy segments
         across demographics, interests, psychographics, and attitudes.
Phase B: Creates and activates audiences via the OpenX GraphQL API.
"""

import streamlit as st
from core.openx_service import OpenXService
from core.openx_mapper import (
    preview_all_segments,
    build_audience_params,
    build_deal_params,
    resolve_segment_ids,
    load_taxonomy,
    TAXONOMY_CSV_PATH,
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


def render_openx_activation():
    """Main entry point — called from the results tab."""

    # ---------- Taxonomy check ----------
    taxonomy = load_taxonomy()
    if not taxonomy:
        st.info(
            f"**Segment Taxonomy** not found.\n\n"
            f"Place the taxonomy CSV at `{TAXONOMY_CSV_PATH}`."
        )
        return

    # ---------- API config check ----------
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
        "Select the segments you want to activate."
    )

    # Generate previews (once)
    if st.session_state.get("openx_mapping_preview") is None:
        with st.spinner("Matching ARI segments to taxonomy..."):
            previews = preview_all_segments(dict(st.session_state))
            st.session_state.openx_mapping_preview = previews

    previews = st.session_state.openx_mapping_preview or []

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

        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            selected[idx] = st.checkbox("", value=True, key=f"openx_sel_{idx}")
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

                # --- 2. Location ---
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

                # --- 4. Language ---
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

                st.markdown("**Mosaic Persona**")
                _render_trait_matches("Mosaic Persona", matches.get("mosaic_persona", []))

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

                # Warnings
                if warnings:
                    for w in warnings:
                        st.warning(w, icon="⚠️")

    # ---------- Phase B: Audience Creation ----------
    st.markdown("---")

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
        st.rerun()
