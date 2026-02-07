from django.urls import path
from .views import certificate_view, download_certificate

urlpatterns = [
    path("<int:course_id>/", certificate_view, name="certificate"),
    path("download/<int:course_id>/", download_certificate),
]
