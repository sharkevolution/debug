# Generated by Django 4.0 on 2023-04-19 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_alter_room_name_alter_room_participante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
