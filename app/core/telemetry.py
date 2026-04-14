def emit(event_type: str, **kwargs):
    print({
        "event": event_type,
        **kwargs
    })
