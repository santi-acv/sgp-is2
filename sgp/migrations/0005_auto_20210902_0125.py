# Generated by Django 3.2.6 on 2021-09-02 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0004_proyecto'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='creador',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='duracion_sprint',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='descripcion',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='fecha_fin',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='fecha_inicio',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='status',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('iniciado', 'Iniciado'), ('finalizado', 'Finalizado'), ('cancelado', 'Cancelado')], max_length=50, null=True),
        ),
    ]