from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

SERVICE_CHOICES = (
    ("AC Services", "AC Services"),
    ("Car care Services", "Car care Services"),
    ("Body Repair", "Body Repair"),
    
    )
TIME_CHOICES = (
    ("8 AM", "8 AM"),
    ("11 AM", "11 AM"),
    ("3 PM", "3 PM"),
    ("6 PM", "6 PM"),
    ("9 PM", "9 PM"),
    
)

BRAND_CHOICES = (
    ("Hyundai", "Hyundai"),
    ("Toyota", "Toyota"),
    ("Ford", "Ford"),
    ("Mahindra", "Mahindra"),
    ("Skoda", "Skoda"),
    ("Honda", "Honda"),
    ("Tata", "Tata"),
    ("Maruti Suzuki", "Maruti Suzuki"),
)


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, default="Body Repair")
    day = models.DateField(default=datetime.now)
    time = models.CharField(max_length=10, choices=TIME_CHOICES, default="3 PM")
    time_ordered = models.DateTimeField(default=datetime.now, blank=True)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES, default="Tata")
    def __str__(self):
        return f"{self.user.username} | day: {self.day} | time: {self.time}"