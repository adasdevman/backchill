from django.db import migrations, models
from django.utils.text import slugify

def generate_usernames(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for user in User.objects.filter(username__isnull=True):
        base_username = user.email.split('@')[0] if user.email else 'user'
        username = slugify(base_username)
        counter = 1
        temp_username = username
        while User.objects.filter(username=temp_username).exists():
            temp_username = f"{username}{counter}"
            counter += 1
        user.username = temp_username
        user.save()

def reverse_generate_usernames(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(default='user', max_length=150, unique=True),
            preserve_default=False,
        ),
        migrations.RunPython(
            generate_usernames,
            reverse_generate_usernames
        ),
    ] 