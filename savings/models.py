from django.conf import settings
from django.db import models

class Member(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="member_profile")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

class Contribution(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="contributions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    contribution_date = models.DateField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="recorded_contributions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-contribution_date", "-created_at"]

    def __str__(self):
        return f"{self.member.full_name} - {self.amount} on {self.contribution_date}"


class AjoPayout(models.Model):
    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_COMPLETED, "Completed"),
    ]

    round_number = models.PositiveIntegerField(unique=True)
    recipient = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="payouts")
    scheduled_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    payout_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_ajo_payouts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["round_number"]

    def __str__(self):
        return f"Round {self.round_number} - {self.recipient.full_name}"


class GroupSettings(models.Model):
    FREQUENCY_CHOICES = [("Daily", "Daily"), ("Weekly", "Weekly"), ("Monthly", "Monthly")]
    group_name = models.CharField(max_length=150, default="ContriTrack Savings Circle")
    contribution_amount = models.DecimalField(max_digits=12, decimal_places=2, default=5000)
    contribution_frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="Weekly")
    start_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.group_name

    @classmethod
    def current(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings
