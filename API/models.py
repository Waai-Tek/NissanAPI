from django.db import models


# Create your models here.
class BaseJourney(models.Model):
    Name = models.CharField(max_length=255)
    JourneyDescription = models.TextField(blank=True, null=True)
    CreatedOn = models.DateTimeField()
    ModifiedOn = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.Name
