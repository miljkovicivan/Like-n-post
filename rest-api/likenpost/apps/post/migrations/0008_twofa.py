# Generated by Django 2.0 on 2018-02-21 16:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0007_auto_20180121_1257'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwoFA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('secret', models.CharField(max_length=32)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='two_fa', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
