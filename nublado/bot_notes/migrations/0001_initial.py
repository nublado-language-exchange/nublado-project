# Generated by Django 4.0 on 2022-04-25 16:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GroupNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='date updated')),
                ('group_id', models.BigIntegerField()),
                ('note_tag', models.CharField(max_length=255)),
                ('message_id', models.BigIntegerField(null=True)),
                ('content', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Bot note',
                'verbose_name_plural': 'Bot notes',
                'unique_together': {('group_id', 'note_tag')},
            },
        ),
    ]
