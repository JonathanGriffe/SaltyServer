# Generated by Django 3.1.5 on 2021-02-07 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0005_auto_20210203_1023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='champion',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='status',
            name='blue',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='status',
            name='red',
            field=models.CharField(max_length=50),
        ),
    ]