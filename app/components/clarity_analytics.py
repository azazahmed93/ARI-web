import streamlit.components.v1 as components

CLARITY_ID = "wnympy1cy9"


def clarity_analytics():
    """Inject the Microsoft Clarity tracking script into the parent Streamlit document."""
    components.html(
        f"""
        <script>
        (function() {{
            var parentDoc = window.parent.document;
            if (parentDoc.getElementById("clarity-{CLARITY_ID}")) return;
            var c = window.parent;
            c["clarity"] = c["clarity"] || function() {{
                (c["clarity"].q = c["clarity"].q || []).push(arguments);
            }};
            var t = parentDoc.createElement("script");
            t.id = "clarity-{CLARITY_ID}";
            t.async = 1;
            t.src = "https://www.clarity.ms/tag/{CLARITY_ID}";
            var y = parentDoc.getElementsByTagName("script")[0];
            y.parentNode.insertBefore(t, y);
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
