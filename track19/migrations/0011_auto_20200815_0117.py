# Generated by Django 3.0.8 on 2020-08-15 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track19', '0010_auto_20200815_0107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rolluplocationattrrecentdelta',
            name='attr',
            field=models.TextField(),
        ),
        migrations.AlterUniqueTogether(
            name='rolluplocationattrrecentdelta',
            unique_together={('token', 'attr')},
        ),
    ]