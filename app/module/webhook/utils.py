def parse_push_event(payload):
    """Parse GitHub push event."""
    # Get commit data
    commits = payload.get("commits", [])
    if not commits:
        # Handle empty push (branch creation, etc.)
        head_commit = payload.get("head_commit", {})
        author = head_commit.get("author", {}).get("name") if head_commit else "unknown"
        commit_hash = payload.get("after", "unknown")[:7]
    else:
        # Use first commit's author
        author = commits[0].get("author", {}).get("name", "unknown")
        commit_hash = commits[0].get("id", "unknown")[:7]
    
    # Get branch name (ref format: refs/heads/branch-name)
    ref = payload.get("ref", "")
    to_branch = ref.replace("refs/heads/", "") if ref else "unknown"
    
    # UTC timestamp
    timestamp = datetime.now(timezone.utc)
    
    return {
        "request_id": commit_hash,
        "author": author,
        "action": "PUSH",
        "from_branch": None,  # Push doesn't have from_branch
        "to_branch": to_branch,
        "timestamp": timestamp,
        "display_time": format_timestamp(timestamp)
    }


def parse_pull_request_event(payload):
    """Parse GitHub pull_request event."""
    pr = payload.get("pull_request", {})
    action = payload.get("action", "")
    
    # Get author
    author = pr.get("user", {}).get("login", "unknown")
    
    # Get branches
    from_branch = pr.get("head", {}).get("ref", "unknown")
    to_branch = pr.get("base", {}).get("ref", "unknown")
    
    # PR number as request_id
    pr_number = pr.get("number", "unknown")
    
    # UTC timestamp
    timestamp = datetime.now(timezone.utc)
    
    # Determine if it's a merge or just a PR submission
    merged = pr.get("merged", False)
    
    if action == "opened":
        # New PR submitted
        return {
            "request_id": f"PR-{pr_number}",
            "author": author,
            "action": "PULL_REQUEST",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "display_time": format_timestamp(timestamp)
        }
    
    elif action == "closed" and merged:
        # PR was merged (bonus brownie points)
        return {
            "request_id": f"MERGE-{pr_number}",
            "author": author,
            "action": "MERGE",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "display_time": format_timestamp(timestamp)
        }
    
    else:
        # PR closed without merge or other actions - ignore
        return None