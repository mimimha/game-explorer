from django.conf import settings
from django.db import models


class Wishlist(models.Model):
    """ERD Wishlist(wishlist_id, user_id, game_id) — User↔Game 찜 조인."""
    wishlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='wishlists', db_column='user_id',
    )
    game = models.ForeignKey(
        'games.Game', on_delete=models.CASCADE,
        related_name='wishlisted_by', db_column='game_id',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlist'
        ordering = ['-wishlist_id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'game'], name='unique_wishlist'
            ),
        ]

    def __str__(self):
        return f'{self.user} ♥ {self.game}'
