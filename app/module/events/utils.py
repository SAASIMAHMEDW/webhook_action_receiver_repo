def format_event_message(event):
    """Format event into human-readable message."""
    action = event.get("action")
    author = event.get("author")
    from_branch = event.get("from_branch")
    to_branch = event.get("to_branch")
    display_time = event.get("display_time", "")
    
    if action == "PUSH":
        return f'{author} pushed to "{to_branch}" on {display_time}'
    
    elif action == "PULL_REQUEST":
        return f'{author} submitted a pull request from "{from_branch}" to "{to_branch}" on {display_time}'
    
    elif action == "MERGE":
        return f'{author} merged branch "{from_branch}" to "{to_branch}" on {display_time}'
    
    return f"Unknown event by {author}"