# Generated by Django 3.1.7 on 2021-03-02 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('Hid', models.IntegerField(primary_key=True, serialize=False)),
                ('Hname', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('Pid', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('Pname', models.CharField(max_length=255)),
                ('Ppassword', models.CharField(max_length=255)),
                ('Pemail', models.CharField(max_length=255)),
            ],
        ),
    ]
