import os

_initialized = False


def init_rollbar():
    """Initialise Rollbar server-side error monitoring.

    Only activates when ROLLBAR_ACCESS_TOKEN is set (i.e. on deployed
    environments where the platform provides it). Local runs without the
    env var are a no-op, matching how Clarity is gated to deployed URLs.
    """
    global _initialized
    if _initialized:
        return

    token = os.environ.get("ROLLBAR_ACCESS_TOKEN")
    if not token:
        return

    import rollbar

    rollbar.init(
        token,
        environment=os.environ.get("ROLLBAR_ENVIRONMENT", "production"),
        handler="async",
        allow_logging_basic_config=False,
    )
    _initialized = True


def report_exception():
    """Report the currently handled exception to Rollbar (no-op if inactive)."""
    if _initialized:
        import rollbar

        rollbar.report_exc_info()
