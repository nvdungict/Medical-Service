from django.db import models
from user.models import User
# Create your models here.

class Service(models.Model):
    service_id = models.CharField(max_length=8, primary_key=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    service_name = models.CharField(max_length=50, null=True)
    service_type = models.CharField(max_length=30, null=True)
    status = models.IntegerField(default=2)
    total_order = models.IntegerField(default=0)
    total_payment = models.IntegerField(default=0)
    lastbooking_date = models.DateField(null=True)

    def __str__(self):
        return self.service_id

class Doctor(models.Model):
    doctor_id = models.CharField(max_length=8, primary_key=True)
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=50, null=True)
    cccd = models.CharField(max_length=50, null=True)
    contact_number = models.CharField(max_length=20, null=True)
    dob = models.DateField(null=True)
    gender = models.IntegerField(null=True)
    status = models.IntegerField(null=True, default=1)
    service = models.ManyToManyField(Service)   

    def __str__(self):
        return f'{self.firstname} {self.lastname}'

class Membership(models.Model):
    membership_id = models.CharField(max_length=8, primary_key=True, default="TYPE003")
    discount_percent = models.IntegerField(null=True)
    type = models.CharField(max_length=20, default=3)

class Patient(models.Model):
    patient_id = models.BigAutoField(primary_key=True, db_index=False)
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    gender = models.IntegerField(null=True)
    membership = models.ForeignKey(Membership, null=True, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    dob = models.DateField(default='2004-01-01')
    contact_number = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=50, null=True)
    cccd = models.CharField(max_length=50, null=True)
    bmi = models.FloatField(max_length=20, null=True, blank=True)
    weight = models.FloatField(max_length=20, null=True, blank=True)
    height = models.FloatField(max_length=20, null=True, blank=True)
    blood_pressure = models.FloatField(max_length=20, null=True, blank=True)
    total_order = models.IntegerField(default=0)
    total_payment = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Room(models.Model):
    room_id = models.CharField(max_length=8, primary_key=True)
    room_name = models.CharField(max_length=50, null=True)
    room_type = models.CharField(max_length=10, null=True)
    status = models.IntegerField(default=1)
    service = models.ForeignKey(Service, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.room_name

class Appointment(models.Model):
    appointment_id = models.BigAutoField(primary_key=True)
    appointment_date = models.DateField(max_length=20, null=True)
    start_time = models.TimeField(null=True)
    status = models.IntegerField(null=True)
    doctor = models.ForeignKey(Doctor, null=True, on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, null=True, on_delete=models.DO_NOTHING)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    created = models.DateField(auto_now=True, null=True)

    def __int__(self):
        return self.appointment_id

class Prescription(models.Model):
    appointment_id = models.OneToOneField(Appointment, on_delete=models.CASCADE, primary_key=True)
    date_prescribled = models.DateTimeField(null=True)
    dosage = models.CharField(max_length=50, null=True)
    instruction = models.TextField(null=True)

    def __str__(self):
        return self.appointment_id
