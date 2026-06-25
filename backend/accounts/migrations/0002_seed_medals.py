"""7개 메달 카탈로그 초기 데이터 삽입."""
from django.db import migrations

MEDALS = [
    ('발자국 시작',     '서비스에 회원가입 완료'),
    ('첫 번째 발걸음', '첫 번째 게임 찜하기'),
    ('탐험대의 일원',  '프로필 정보 수정 처음 완료'),
    ('첫 교신',        '커뮤니티 게시글 첫 작성'),
    ('수집광',         '찜한 게임 10개 달성'),
    ('댓글 요정',      '댓글 20개 작성'),
    ('전설의 탐험가',  '모든 업적 달성'),
]


def seed(apps, schema_editor):
    Medal = apps.get_model('accounts', 'Medal')
    for name, desc in MEDALS:
        Medal.objects.get_or_create(medal_name=name, defaults={'description': desc})


def unseed(apps, schema_editor):
    Medal = apps.get_model('accounts', 'Medal')
    Medal.objects.filter(medal_name__in=[m[0] for m in MEDALS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
