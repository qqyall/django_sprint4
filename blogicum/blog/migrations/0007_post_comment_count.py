# Generated by Django 3.2.16 on 2024-02-15 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20240214_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comment_count',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]