from django.db import migrations, models
from django.utils.text import slugify
from django.utils import timezone

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

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=timezone.now, verbose_name='date joined')),
                ('username', models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('role', models.CharField(choices=[('ADMIN', 'Administrateur'), ('ANNONCEUR', 'Annonceur'), ('UTILISATEUR', 'Utilisateur')], default='UTILISATEUR', max_length=20)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('banner_image', models.ImageField(blank=True, null=True, upload_to='banner_images/')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.RunPython(
            generate_usernames,
            reverse_code=migrations.RunPython.noop
        ),
    ] 