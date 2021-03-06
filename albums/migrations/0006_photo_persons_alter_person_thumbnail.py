# Generated by Django 4.0.4 on 2022-06-15 13:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('albums', '0005_person_thumbnail'),
    ]

    operations = [
        migrations.AddField(
                model_name='photo',
                name='persons',
                field=models.ManyToManyField(blank=True, to='albums.person'),
        ),
        migrations.AlterField(
                model_name='person',
                name='thumbnail',
                field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                        related_name='thumbnail', to='albums.photo'),
        ),
    ]
