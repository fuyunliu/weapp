from django.contrib.auth import get_user_model
from celery import shared_task


@shared_task
def destroy_user(user_id):
    user = get_user_model().objects.get(user_id)
    user.delete()
