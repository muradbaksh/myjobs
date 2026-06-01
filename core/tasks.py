from celery import shared_task

@shared_task
def send_notification(
    user_id,
    message
):

    print(
        f"""
        Notification sent to:
        {user_id}

        MESSAGE:
        {message}
        """
    )

    return "Notification Sent"