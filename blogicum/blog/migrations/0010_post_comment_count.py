# Generated by Django 3.2.16 on 2024-02-15 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_remove_post_comment_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comment_count',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
