# Generated by Django 3.2.16 on 2024-02-15 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_post_comment_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='comment_count',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
