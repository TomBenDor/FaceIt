from albums.models import Permission


def get_access_to_album(user, album):
    if not user.is_authenticated:
        return Permission.AccessLevel.READ if album.allow_anonymous_view else None

    if album.owner == user:
        return Permission.AccessLevel.MANAGE

    if Permission.objects.filter(user=user, album=album).exists():
        return Permission.objects.get(user=user, album=album).access

    return Permission.AccessLevel.READ if album.allow_anonymous_view else None
