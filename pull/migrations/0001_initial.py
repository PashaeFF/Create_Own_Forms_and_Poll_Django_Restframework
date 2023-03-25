# Generated by Django 4.1.7 on 2023-03-25 11:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pull',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pull_name', models.CharField(max_length=250, unique=True)),
                ('answers', models.JSONField(default=dict)),
                ('count', models.IntegerField(default=0)),
                ('image', models.ImageField(null=True, upload_to='media/images/')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='owner_id')),
            ],
            options={
                'db_table': 'pull',
            },
        ),
    ]