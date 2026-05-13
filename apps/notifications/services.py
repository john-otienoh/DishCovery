from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    User = get_user_model()


def create_notification(
    *,
    recipient,
    actor=None,
    verb: str,
    notification_type: str = "system",
    target_id: int | None = None,
) -> None:
    """
    Create a Notification record.  Import is deferred to avoid
    circular dependency at module load time.
    """
    from .models import Notification

    if actor and actor == recipient:
        return

    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        notification_type=notification_type,
        target_id=target_id,
    )