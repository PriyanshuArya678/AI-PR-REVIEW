def process_pull_request(owner: str, repo: str, number: int) -> None:
    """Orchestrate a single PR review. STUB for now.

    This is the one choke point every trigger (webhook, CLI, future scheduled
    runs) funnels through. Later stages fill it in:
        1. fetch PR metadata + diff   (github.client)
        2. filter / chunk the diff    (review.diff)
        3. run the LLM review         (review.reviewer)
        4. render markdown            (review.render)
        5. post / upsert the comment  (github.client)

    When we add Celery, we wrap THIS function as a task; the webhook layer
    won't change.
    """
    print(f"[pipeline] would review PR {owner}/{repo}#{number}")
