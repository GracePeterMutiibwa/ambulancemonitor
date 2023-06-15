# Generated by Django 4.2.2 on 2023-06-15 07:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssetRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assetId', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hospitalName', models.TextField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='OperationHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serviceDate', models.DateField(auto_now=True)),
                ('requestingHospital', models.TextField(max_length=200)),
                ('assetRequestedLicensePlate', models.TextField(max_length=200)),
                ('controlPersonnel', models.TextField(max_length=200)),
                ('requestTime', models.TimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='HospitalOfficers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeEmail', models.TextField(max_length=200)),
                ('employeePassword', models.TextField(max_length=45)),
                ('employeeHospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authenticatedPersonnel', to='ambuadmin.hospital')),
            ],
        ),
        migrations.CreateModel(
            name='AmbulanceAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assetCategory', models.TextField(max_length=200)),
                ('assetLicensePlate', models.TextField(max_length=200)),
                ('assetSittingCapacity', models.IntegerField()),
                ('serviceStatus', models.BooleanField()),
                ('assetOwner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='available_assets', to='ambuadmin.hospital')),
            ],
        ),
    ]
