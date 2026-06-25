from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from github.security import verify_signature
from pipeline.process import process_pull_request

router = APIRouter()

# GitHub PR actions worth reviewing. We ignore the rest (e.g. "labeled",
# "assigned", "closed") so we don't waste LLM calls on no-op events.
#   opened      -> a new PR was created
#   synchronize -> new commits were pushed to an existing PR
#   reopened    -> a closed PR was reopened
RELEVANT_ACTIONS = {"opened", "synchronize", "reopened"}


@router.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str | None = Header(default=None),
):
    # 1. Read the RAW body first — the signature is computed over these exact
    #    bytes. Parsing to JSON and re-serializing would change whitespace and
    #    break the comparison.
    raw = await request.body()

    # 2. Authenticate: prove this request actually came from GitHub.
    if not verify_signature(raw, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="invalid signature")

    # 3. Filter by event type. The X-GitHub-Event header tells us the kind of
    #    event; we only handle pull requests.
    if x_github_event != "pull_request":
        return {"status": "ignored", "reason": f"event={x_github_event}"}

    # 4. Parse the payload and filter by action.
    payload = await request.json()
    action = payload.get("action")
    if action not in RELEVANT_ACTIONS:
        return {"status": "ignored", "reason": f"action={action}"}

    # 5. Pull out the four things we actually need.
    owner, repo = payload["repository"]["full_name"].split("/")
    number = payload["pull_request"]["number"]

    # 6. Hand off the slow work to the background and ACK immediately. GitHub
    #    times out webhooks after ~10s, but an LLM review takes far longer — so
    #    we must never review inline here. (Later: replace with Celery .delay().)
    background_tasks.add_task(process_pull_request, owner, repo, number)

    return {"status": "accepted", "pr": f"{owner}/{repo}#{number}"}
