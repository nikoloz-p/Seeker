# Generated by Django 5.2.3 on 2025-07-06 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_hrge_jobsge_myjobsge_delete_job_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/', verbose_name='Profile Pic'),
        ),
    ]
