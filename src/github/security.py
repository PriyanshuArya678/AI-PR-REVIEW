import hashlib
import hmac

from core.config import settings


def verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Verify GitHub's X-Hub-Signature-256 header against the raw request body.

    GitHub signs every webhook payload with HMAC-SHA256, keyed by the shared
    secret we configured on the webhook. We recompute that signature over the
    *raw bytes* we received and compare. If they match, the request really came
    from GitHub (only GitHub and we know the secret).
    """
    if not signature_header:
        return False

    expected = "sha256=" + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    # constant-time compare avoids leaking info via response timing
    return hmac.compare_digest(expected, signature_header)
