from django.db import models
from django.utils import timezone


class Translation(models.Model):
    keyword = models.CharField(max_length=5000)
    english = models.CharField(max_length=5000, blank=True, null=True)
    serbian = models.CharField(max_length=5000, blank=True, null=True)
    russian = models.CharField(max_length=5000, blank=True, null=True)
    chinese = models.CharField(max_length=5000, blank=True, null=True)

    def __str__(self):
        return self.keyword


class Client(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    logged_in = models.BooleanField(default=False, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    hashed_email_and_password = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    cycle_type = models.CharField(max_length=50, blank=True, null=True)
    password_reset_code = models.IntegerField(null=True, blank=True)
    period_length = models.IntegerField(null=True, blank=True)
    menstrual_cyclus_length = models.IntegerField(null=True, blank=True)
    dass_tests_taken = models.IntegerField(default=0, null=True, blank=True)
    total_dass_tests_number = models.IntegerField(default=0, null=True, blank=True)
    user_token = models.CharField(max_length=50, blank=True, null=True)
    notification_token = models.CharField(max_length=500, blank=True, null=True)
    profile_image = models.CharField(max_length=500, blank=True, null=True)
    period_dates = models.JSONField(null=True, blank=True)
    disability = models.BooleanField(default=False, null=True, blank=True)
    genetic_disorder = models.BooleanField(default=False, null=True, blank=True)
    last_dass_test_date = models.DateField(blank=True, null=True)
    next_dass_test_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    existing = models.BooleanField(default=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Notification(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('hidden', 'Hidden'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notifications')
    notification_title = models.CharField(max_length=255)
    notification_text = models.TextField()
    notification_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    notification_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    cycle_reminder = models.BooleanField(default=False, blank=True, null=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client} - {self.notification_title}"


class TestResult(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='test_results')
    test_type_id = models.IntegerField()
    raw_test_result = models.JSONField()
    final_test_result = models.JSONField()
    test_taken_at = models.DateTimeField(default=timezone.now)
    test_ordinal_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Test for {self.client} - Type {self.test_type_id}"


class AdminUser(models.Model):
    email = models.EmailField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=254, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.email or "Admin"


class CustomerNote(models.Model):
    customer = models.ForeignKey(Client, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=255, blank=True, null=True)
    note_text = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.note_title or "Note"
