# Generated by Django 4.0.4 on 2022-06-12 20:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('albums', '0002_alter_album_id_alter_photo_id'),
    ]

    operations = [
        migrations.AddField(
                model_name='person',
                name='nameable',
                field=models.BooleanField(default=False),
        ),
    ]
