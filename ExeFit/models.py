from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.core.validators import MinValueValidator
import uuid

class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=[('yearly', 'Yearly')], default='yearly')
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    duration_days = models.IntegerField(default=365, editable=False)  # Fixed to 365 days
    tx_hash = models.CharField(max_length=100, default='0x0000000')  # Store the transaction hash
    membership_status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Yearly Membership - £{self.price}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)
    membership_start = models.DateField(null=True, blank=True)
    membership_end = models.DateField(null=True, blank=True)
    check_in_count = models.IntegerField(default=0)

    def is_membership_active(self):
        return self.membership_end and self.membership_end >= now().date()

    def __str__(self):
        return self.user.username

class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    duration_minutes = models.IntegerField()

    def __str__(self):
        return self.name

class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('booked', 'Booked'), ('cancelled', 'Cancelled')], default='booked')

    def __str__(self):
        return f"{self.user.username} - {self.activity.name} on {self.date} at {self.time}"

class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    checkin_time = models.DateTimeField(default=now)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6)
    location_long = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"{self.user.username} - {self.activity.name} @ {self.checkin_time}"

class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start = models.DateField()
    week_end = models.DateField()
    workouts_count = models.IntegerField(default=0)
    reward_earned = models.BooleanField(default=False)

    def check_eligibility(self):
        if self.workouts_count >= 4:
            self.reward_earned = True
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.week_start} to {self.week_end} - {'Earned' if self.reward_earned else 'Not Earned'}"

class SmartContractExecution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    transaction_hash = models.CharField(max_length=66, unique=True, null=True, blank=True)  # Ethereum Tx Hash
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_hash}"

