from django.contrib import admin
from .models import (
    Course,
    Section,
    Lesson,
    Enrollment,
    LessonProgress,
    CourseReview,
)

# --------------------
# COURSE
# --------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "published", "created_at")
    list_filter = ("published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)


# --------------------
# SECTION
# --------------------
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    list_filter = ("course",)
    search_fields = ("title",)


# --------------------
# LESSON
# --------------------
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "course_name")
    list_filter = ("section__course",)
    search_fields = ("title",)

    def course_name(self, obj):
        return obj.section.course.title

    course_name.short_description = "Course"


# --------------------
# ENROLLMENT
# --------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "paid", "enrolled_at")
    list_filter = ("paid", "course")
    search_fields = ("user__username", "course__title")


# --------------------
# LESSON PROGRESS
# --------------------
@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed")
    list_filter = ("completed", "lesson__section__course")
    search_fields = ("user__username", "lesson__title")


# --------------------
# COURSE REVIEWS
# --------------------
@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "rating", "created_at")
    list_filter = ("rating", "course")
    search_fields = ("course__title", "user__username")
    ordering = ("-created_at",)
