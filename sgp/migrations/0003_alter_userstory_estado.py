# Generated by Django 3.2.6 on 2021-10-23 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0002_rename_horas_disponibles_participasprint_horas_diarias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstory',
            name='estado',
            field=models.CharField(choices=[('P', 'Pendiente'), ('I', 'Iniciado'), ('Q', 'Q&A'), ('F', 'Finalizado'), ('C', 'Cancelado')], default='P', max_length=50),
        ),
    ]