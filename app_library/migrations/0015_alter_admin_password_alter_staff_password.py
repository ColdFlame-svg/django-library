# Generated by Django 5.1.1 on 2025-01-02 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_library', '0014_alter_admin_password_alter_staff_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$mXNQFekpwoo29tlyTNES35$AEx7YgTxXqg5Z4s6wHO9499iFxCq/b4NIn6rN7eX548=', max_length=128),
        ),
        migrations.AlterField(
            model_name='staff',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$p4eMnydcmYwYsy5kq5x2Q2$vd7Rx9U/O/pFHhjDHl20PnJy4sVHOOJR7U+TSsbzvN8=', max_length=128),
        ),
    ]
