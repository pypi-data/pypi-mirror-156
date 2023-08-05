# Generated by Django 3.2.4 on 2021-06-24 22:52

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import rgd.models.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rgd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointCloud',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('failure_reason', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('created', 'Created but not queued'),
                            ('queued', 'Queued for processing'),
                            ('running', 'Processing'),
                            ('failed', 'Failed'),
                            ('success', 'Succeeded'),
                        ],
                        default='created',
                        max_length=20,
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                (
                    'file',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='+',
                        to='rgd.checksumfile',
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=(models.Model, rgd.models.mixins.PermissionPathMixin),
        ),
        migrations.CreateModel(
            name='PointCloudSpatial',
            fields=[
                (
                    'spatialentry_ptr',
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='rgd.spatialentry',
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('crs', models.TextField(blank=True, help_text='PROJ string', null=True)),
                (
                    'origin',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), blank=True, null=True, size=3
                    ),
                ),
                (
                    'source',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='rgd_3d.pointcloud'
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('rgd.spatialentry', models.Model, rgd.models.mixins.PermissionPathMixin),
        ),
        migrations.CreateModel(
            name='PointCloudMeta',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=1000)),
                ('description', models.TextField(blank=True, null=True)),
                (
                    'source',
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='rgd_3d.pointcloud',
                    ),
                ),
                (
                    'vtp_data',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='+',
                        to='rgd.checksumfile',
                    ),
                ),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=(
                models.Model,
                rgd.models.mixins.PermissionPathMixin,
                rgd.models.mixins.DetailViewMixin,
            ),
        ),
    ]
