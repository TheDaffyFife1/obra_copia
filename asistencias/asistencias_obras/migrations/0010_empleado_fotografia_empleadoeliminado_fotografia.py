# Generated by Django 5.0.3 on 2024-03-11 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asistencias_obras', '0009_obra_activa_obra_fecha_fin_obra_fecha_inicio'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='fotografia',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_empleados/', verbose_name='Fotografía'),
        ),
        migrations.AddField(
            model_name='empleadoeliminado',
            name='fotografia',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_empleados/', verbose_name='Fotografía'),
        ),
    ]
