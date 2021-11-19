# Generated by Django 3.2.6 on 2021-11-19 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0005_incremento_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='incremento',
            name='estado',
            field=models.CharField(choices=[('P', 'Pendiente'), ('I', 'Iniciado'), ('Q', 'Quality Assurance'), ('F', 'Finalizado'), ('C', 'Cancelado')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='userstory',
            name='estado',
            field=models.CharField(choices=[('P', 'Pendiente'), ('I', 'Iniciado'), ('Q', 'Quality Assurance'), ('F', 'Finalizado'), ('C', 'Cancelado')], default='P', max_length=50),
        ),
    ]
