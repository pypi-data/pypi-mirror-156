# Generated by Django 3.2.9 on 2021-11-16 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgd', '0005_auto_20211105_1715'),
        ('rgd_3d', '0002_alter_pointcloud_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PointCloud',
            new_name='Mesh3D',
        ),
        migrations.RenameModel(
            old_name='PointCloudMeta',
            new_name='Mesh3DMeta',
        ),
        migrations.RenameModel(
            old_name='PointCloudSpatial',
            new_name='Mesh3DSpatial',
        ),
    ]
