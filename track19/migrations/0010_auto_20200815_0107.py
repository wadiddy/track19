# Generated by Django 3.0.8 on 2020-08-15 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track19', '0009_rolluplocationattrrecentdelta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rolluplocationattrrecentdelta',
            name='latest_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='rolluplocationattrrecentdelta',
            name='month_ago_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='rolluplocationattrrecentdelta',
            name='two_weeks_ago_date',
            field=models.DateField(null=True),
        ),
    ]
