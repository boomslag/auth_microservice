# Generated by Django 3.2.16 on 2023-01-30 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20230130_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='buyers',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='products',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
