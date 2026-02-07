from django.urls import path
from .views import *

urlpatterns = [
    path('', course_list, name='course_list'),
    path("<int:course_id>/", course_detail, name="course_detail"),

    path("lesson/<int:lesson_id>/", lesson_view, name="lesson"),
    path("lesson/complete/<int:lesson_id>/", complete_lesson, name="complete_lesson"),
    path("review/<int:course_id>/", add_review, name="add_review"),

    path('continue/<int:course_id>/', continue_learning, name='continue_learning'),
]
