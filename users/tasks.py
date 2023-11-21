from celery import shared_task

from django.core.management import call_command


@shared_task
def flush_expired_tokens() -> None:
    call_command("flushexpiredtokens")

    print("Expired tokens flushed.")
