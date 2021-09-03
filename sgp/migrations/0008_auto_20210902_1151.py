# Generated by Django 3.2.6 on 2021-09-02 15:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0007_auto_20210902_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyecto',
            name='creador',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='duracion_sprint',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='fecha_fin',
            field=models.DateField(null=True),
        ),
    ]