# Generated by Django 3.0.8 on 2020-08-15 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track19', '0011_auto_20200815_0117'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolluplocationattrrecentdelta',
            name='id',
            field=models.AutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='rolluplocationattrrecentdelta',
            name='token',
            field=models.TextField(),
        ),
    ]
