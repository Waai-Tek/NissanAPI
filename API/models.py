from django.db import models


# Create your models here.
class Devices(models.Model):
    Name = models.CharField(max_length=255)
    Location = models.TextField(blank=True, null=True)
    CreatedOn = models.DateTimeField()
    ModifiedOn = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.Name


class DeviceAnalytics(models.Model):
    DeviceID = models.ForeignKey(Devices, on_delete=models.CASCADE)
    NetworkStatus = models.BooleanField()
    Status = models.BooleanField()
    InsertedOn = models.DateTimeField()


class ActiveObjects(models.Model):
    Name = models.CharField(max_length=255)
    DeviceID = models.ForeignKey(Devices, on_delete=models.CASCADE)
    Keyword = models.CharField(max_length=255)
    InsertedOn = models.DateTimeField()

    def __str__(self):
        return self.Name


class QuickLinks(models.Model):
    Name = models.CharField(max_length=255)
    DeviceID = models.ForeignKey(Devices, on_delete=models.CASCADE)
    InsertedOn = models.DateTimeField()

    def __str__(self):
        return self.Name
