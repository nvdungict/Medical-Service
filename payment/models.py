from django.db import models
from service.models import Appointment

# Create your models here.
class Payment(models.Model):
    appointment_id = models.OneToOneField(Appointment, on_delete=models.CASCADE, primary_key=True)
    payment_time = models.DateTimeField(null=True,auto_now=True)
    status = models.IntegerField(null=True)

    def __str__(self):
        return self.appointment_id