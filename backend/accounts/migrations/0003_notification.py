from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_seed_medals'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notif_type', models.CharField(
                    choices=[
                        ('follow', '팔로우'),
                        ('new_post', '새 게시글'),
                        ('new_wishlist', '찜 추가'),
                        ('medal', '메달 획득'),
                    ],
                    max_length=20,
                )),
                ('target_id', models.IntegerField(blank=True, null=True)),
                ('target_title', models.CharField(blank=True, max_length=200)),
                ('message', models.CharField(max_length=300)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(
                    blank=True, null=True,
                    db_column='actor_id',
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sent_notifications',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('recipient', models.ForeignKey(
                    db_column='recipient_id',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'notification',
                'ordering': ['-created_at'],
            },
        ),
    ]
