# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='accounts.Follow')
def notify_new_follower(sender, instance, created, **kwargs):
    """누군가 나를 팔로우했을 때 → 팔로우 당한 사람에게 알림."""
    if not created:
        return
    from .models import Notification
    Notification.objects.create(
        recipient=instance.following,
        actor=instance.follower,
        notif_type=Notification.Type.FOLLOW,
        message=f'{instance.follower.nickname}님이 회원님을 팔로우하기 시작했습니다.',
    )


@receiver(post_save, sender='community.Post')
def notify_new_post(sender, instance, created, **kwargs):
    """내가 팔로우하는 사람이 새 글을 올렸을 때 → 나에게 알림."""
    if not created:
        return
    from .models import Notification
    # 작성자를 팔로우하는 사람들에게 알림
    followers = instance.user.follower_relations.select_related('follower').all()
    notifs = [
        Notification(
            recipient=rel.follower,
            actor=instance.user,
            notif_type=Notification.Type.NEW_POST,
            target_id=instance.post_id,
            target_title=instance.title,
            message=f'{instance.user.nickname}님이 새 글을 올렸습니다: {instance.title[:40]}',
        )
        for rel in followers
    ]
    if notifs:
        Notification.objects.bulk_create(notifs)


@receiver(post_save, sender='wishlists.Wishlist')
def notify_new_wishlist(sender, instance, created, **kwargs):
    """내가 팔로우하는 사람이 게임을 찜했을 때 → 나에게 알림."""
    if not created:
        return
    from .models import Notification
    followers = instance.user.follower_relations.select_related('follower').all()
    game_title = instance.game.title_ko or instance.game.title
    notifs = [
        Notification(
            recipient=rel.follower,
            actor=instance.user,
            notif_type=Notification.Type.NEW_WISHLIST,
            target_id=instance.game_id,
            target_title=game_title,
            message=f'{instance.user.nickname}님이 {game_title}을(를) 찜했습니다.',
        )
        for rel in followers
    ]
    if notifs:
        Notification.objects.bulk_create(notifs)


@receiver(post_save, sender='accounts.UserMedal')
def notify_medal_earned(sender, instance, created, **kwargs):
    """메달을 획득했을 때 → 본인에게 알림."""
    if not created:
        return
    from .models import Notification
    Notification.objects.create(
        recipient=instance.user,
        notif_type=Notification.Type.MEDAL,
        target_title=instance.medal.medal_name,
        message=f'새 메달을 획득했습니다: {instance.medal.medal_name}',
    )
