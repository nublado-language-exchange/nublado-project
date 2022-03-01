# Generated by Django 4.0 on 2022-02-14 00:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_telegram', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMemberPoints',
            fields=[
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='date updated')),
                ('group_member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='django_telegram.telegramgroupmember')),
                ('points', models.PositiveBigIntegerField(default=0)),
                ('point_increment', models.PositiveBigIntegerField(default=1)),
            ],
            options={
                'verbose_name': 'group member points',
            },
        ),
    ]
