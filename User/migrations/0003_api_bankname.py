# Generated by Django 3.2.6 on 2022-01-14 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0002_api'),
    ]

    operations = [
        migrations.AddField(
            model_name='api',
            name='bankName',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]