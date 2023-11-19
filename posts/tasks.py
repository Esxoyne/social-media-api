from django.utils import timezone

from celery import shared_task

from .models import Post


@shared_task
def defer_post(post_id: int) -> None:
    post = Post.objects.get(pk=post_id)
    post.published = True
    post.created_at = timezone.now()
    post.save()
    print(f"Post {post.id} published.")
