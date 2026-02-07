from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ("SUCCESS", "Success"),
            ("FAILED", "Failed"),
        ),
        default="SUCCESS"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
