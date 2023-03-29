from django.db import models


# Create your models here.

class Person(models.Model):
    Pid = models.CharField(max_length=30, primary_key=True)
    Pname = models.CharField(max_length=255, null=True)
    Ppassword = models.CharField(max_length=255, null=True)
    Pemail = models.CharField(max_length=255, null=True)
    linetoken = models.CharField(max_length=255, null=True)


class Hospital(models.Model):
    Hid = models.IntegerField(primary_key=True)
    Hname = models.CharField(max_length=255, null=True)


class HN(models.Model):
    HNpid = models.CharField(max_length=30, null=True)
    HNhid = models.IntegerField(default=0)
    HN = models.CharField(max_length=50, null=True)
    hncheck = models.IntegerField()

    class Meta:
        unique_together = (("HNpid", "HNhid"),)


class Department(models.Model):
    Did = models.CharField(max_length=30, primary_key=True)
    Dname = models.CharField(max_length=255, null=True)
    Hid = models.IntegerField(default=0)


class Officer(models.Model):
    OFid = models.IntegerField(primary_key=True)
    OFname = models.CharField(max_length=255, null=True)
    Did = models.CharField(max_length=30, null=True)
    Pid = models.CharField(max_length=30, null=True)


class Patient(models.Model):
    Pid = models.CharField(max_length=30, null=True)


class Staff(models.Model):
    Pid = models.CharField(max_length=30, null=True)
    Hid = models.IntegerField(default=0)
    status = models.IntegerField(default=0)


class schedule(models.Model):
    number = models.IntegerField(default=0)
    start = models.DateField(null=True)
    timestart = models.TimeField(null=True)
    timeend = models.TimeField(null=True)
    status = models.IntegerField(default=0)
    OFid = models.IntegerField(default=0)


class hospitaltime(models.Model):
    timestart = models.TimeField(null=True)
    timeend = models.TimeField(null=True)
    start = models.DateField(null=True)
    Hid = models.IntegerField(default=0)
    Did = models.CharField(max_length=30, null=True)


class bookingperson(models.Model):
    Pid = models.CharField(max_length=30)
    schedule_id = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    event = models.CharField(max_length=255, null=True)
    verify = models.DateTimeField(null=True)
    callqueue = models.DateTimeField(null=True)
    reed = models.IntegerField(default=0)
    queuenum = models.IntegerField()
    Did = models.CharField(max_length=12)
    OFid = models.IntegerField()


class tagdepartment(models.Model):
    tags = models.CharField(max_length=255)
    Did = models.CharField(max_length=12)
