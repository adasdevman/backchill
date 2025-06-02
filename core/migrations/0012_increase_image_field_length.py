from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_galerievideo'),  # Using the latest migration found
    ]

    operations = [
        migrations.AlterField(
            model_name='galeriephoto',
            name='image',
            field=models.ImageField(upload_to='annonces/photos/', max_length=500),
        ),
        migrations.AlterField(
            model_name='galerievideo',
            name='video',
            field=models.FileField(upload_to='annonces/videos/', max_length=500),
        ),
    ]
