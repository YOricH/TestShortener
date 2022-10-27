# Generated by Django 4.1.2 on 2022-10-17 16:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Direction',
            fields=[
                (
                    'subpart',
                    models.CharField(max_length=30, primary_key=True, serialize=False),
                ),
                ('target', models.URLField(max_length=2000)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserDirection',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('user_uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                (
                    'direction',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='shortener.direction',
                    ),
                ),
            ],
            options={
                'ordering': ['-timestamp'],
                'unique_together': {('direction', 'user_uuid')},
            },
        ),
    ]
