def format_ms_to_clock(ms: int) -> str:
    """
    Converts milliseconds to an MM:SS string format.
    """
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02}:{seconds:02}"