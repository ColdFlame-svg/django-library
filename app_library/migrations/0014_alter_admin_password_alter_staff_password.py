# Generated by Django 5.1.1 on 2025-01-02 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_library', '0013_alter_admin_password_alter_staff_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$m1bZfsQ1REGtErCA2hKrXZ$pMGW7uDroiTIEW5IFgOnkr+PPRfA3llBXP9702rWjf8=', max_length=128),
        ),
        migrations.AlterField(
            model_name='staff',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$yGuD6UxOP87GIpgTPIgeoQ$Tkq8vIU3pWVoDVC6xUBMO+PX6DwXPiqQvCoMglMV5a4=', max_length=128),
        ),
    ]
