# Generated by Django 5.1.1 on 2024-12-23 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_library', '0004_rename_is_admin_user_is_admin_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$vOIgmjPfrMErdNb6ojWAuL$cORb4w1AApsL8rdNzzr52CpqE//Zgii89wEXSvIROeA=', max_length=128),
        ),
    ]
