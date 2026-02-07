from django.urls import path
from .views import demo_payment

urlpatterns = [
    path("demo-pay/<int:course_id>/", demo_payment, name="demo_payment"),
]
