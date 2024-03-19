# Generated by Django 5.0.3 on 2024-03-18 08:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asistencias_obras', '0014_asistencia_foto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Título')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Fecha de vencimiento')),
                ('completed', models.BooleanField(default=False, verbose_name='Completado')),
                ('obra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='asistencias_obras.obra')),
            ],
            options={
                'verbose_name': 'hito',
                'verbose_name_plural': 'hitos',
            },
        ),
    ]