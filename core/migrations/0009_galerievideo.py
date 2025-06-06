# Generated by Django 5.1.4 on 2025-05-31 11:50

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_galeriephoto_options_alter_payment_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalerieVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='annonces/videos/')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('annonce', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='core.annonce')),
            ],
            options={
                'verbose_name': 'Vidéo',
                'verbose_name_plural': 'Vidéos',
                'ordering': ['-created'],
            },
        ),
    ]
