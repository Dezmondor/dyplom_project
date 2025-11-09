from .models import SupportChat

def unread_messages(request):
    if request.user.is_authenticated and request.user.is_staff:
        count = SupportChat.objects.filter(is_read=False).count()
        return {'unread_messages_count': count}
    return {}
