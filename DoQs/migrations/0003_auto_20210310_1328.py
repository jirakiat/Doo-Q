# Generated by Django 3.1.7 on 2021-03-10 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DoQs', '0002_hn'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('Did', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('Dname', models.CharField(max_length=255)),
                ('Hid', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('OFid', models.IntegerField(primary_key=True, serialize=False)),
                ('OFname', models.CharField(max_length=255)),
                ('Did', models.CharField(max_length=30)),
                ('Pid', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Pid', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('start', models.DateField()),
                ('timestart', models.TimeField()),
                ('timeend', models.TimeField()),
                ('status', models.IntegerField()),
                ('OFid', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Pid', models.CharField(max_length=30)),
                ('Hid', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='hn',
            name='HNhid',
            field=models.IntegerField(),
        ),
    ]
