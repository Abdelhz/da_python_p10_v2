# Generated by Django 5.0.1 on 2024-01-26 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={},
        ),
        migrations.RemoveField(
            model_name='contributor',
            name='date_given_permission',
        ),
        migrations.AddField(
            model_name='contributor',
            name='can_assign_issues',
            field=models.BooleanField(default=False),
        ),
    ]
