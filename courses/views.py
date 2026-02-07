from django.shortcuts import render, get_object_or_404, redirect, render
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import *

def landing_page(request):
    courses = Course.objects.filter(published=True)[:6]
    return render(request, 'landing.html', {'courses': courses})



def course_list(request):
    courses = Course.objects.filter(published=True)

    # ---------- SEARCH ----------
    query = request.GET.get("q")
    if query:
        courses = courses.filter(title__icontains=query)

    # ---------- FILTER ----------
    filter_type = request.GET.get("filter")

    if filter_type == "free":
        courses = courses.filter(price=0)

    elif filter_type == "paid":
        courses = courses.filter(price__gt=0)

    elif filter_type == "enrolled" and request.user.is_authenticated:
        courses = courses.filter(
            enrollments__user=request.user,
            enrollments__paid=True
        )

    # ---------- ENROLLMENT + PROGRESS ----------
    enrolled_courses = {}
    progress_data = {}

    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(
            user=request.user,
            paid=True
        ).values_list("course_id", flat=True)

        enrolled_courses = set(enrollments)

        for course_id in enrolled_courses:
            total = Lesson.objects.filter(
                section__course_id=course_id
            ).count()

            completed = LessonProgress.objects.filter(
                user=request.user,
                lesson__section__course_id=course_id,
                completed=True
            ).count()

            progress = int((completed / total) * 100) if total else 0
            progress_data[course_id] = progress

    return render(request, "courses/list.html", {
        "courses": courses,
        "enrolled_courses": enrolled_courses,
        "progress_data": progress_data,
        "query": query,
        "filter_type": filter_type,
    })

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrolled = False
    progress_percent = 0
    completed_lessons = set()
    next_lesson = None
    reviews = []
    has_reviewed = False

    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
            paid=True
        ).exists()

        lessons = list(
            Lesson.objects.filter(
                section__course=course
            ).order_by("id")
        )

        completed_lessons = set(
            LessonProgress.objects.filter(
                user=request.user,
                lesson__section__course=course,
                completed=True
            ).values_list("lesson_id", flat=True)
        )

        # 🔑 find next lesson to continue
        for lesson in lessons:
            if lesson.id not in completed_lessons:
                next_lesson = lesson
                break

        total = len(lessons)
        done = len(completed_lessons)
        progress_percent = int((done / total) * 100) if total else 0

        reviews = course.reviews.all()
        has_reviewed = course.reviews.filter(
            user=request.user
        ).exists()

    return render(request, "courses/detail.html", {
        "course": course,
        "enrolled": enrolled,
        "progress_percent": progress_percent,
        "completed_lessons": completed_lessons,
        "next_lesson": next_lesson,   # 🔥 KEY
        "reviews": reviews,
        "has_reviewed": has_reviewed,
    })


@login_required
def continue_learning(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not Enrollment.objects.filter(
        user=request.user,
        course=course,
        paid=True
    ).exists():
        return redirect("course_detail", course.id)

    lessons = list(
        Lesson.objects.filter(
            section__course=course
        ).order_by("id")
    )

    for lesson in lessons:
        if not LessonProgress.objects.filter(
            user=request.user,
            lesson=lesson,
            completed=True
        ).exists():
            return redirect("lesson", lesson.id)

    # ✅ ALL LESSONS COMPLETED
    return redirect("course_detail", course.id)

@login_required
def lesson_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course

    # 🔐 Enroll check
    if not Enrollment.objects.filter(
        user=request.user,
        course=course,
        paid=True
    ).exists():
        return redirect("course_detail", course.id)

    # 🔢 All lessons in order
    lessons = Lesson.objects.filter(
        section__course=course
    ).order_by("id")

    lesson_ids = list(lessons.values_list("id", flat=True))
    current_index = lesson_ids.index(lesson.id)

    # 🔒 Check previous lesson completion
    if current_index > 0:
        prev_lesson_id = lesson_ids[current_index - 1]

        prev_completed = LessonProgress.objects.filter(
            user=request.user,
            lesson_id=prev_lesson_id,
            completed=True
        ).exists()

        if not prev_completed:
            # ❌ Block skipping
            return redirect("lesson", lesson_ids[0])

    return render(request, "courses/lesson.html", {
        "lesson": lesson,
        "course": course,
        "lessons": lessons,
    })

@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course

    # Enrolled check
    if not Enrollment.objects.filter(
        user=request.user,
        course=course,
        paid=True
    ).exists():
        return redirect("course_detail", course.id)

    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    progress.completed = True
    progress.save()

    return redirect("continue_learning", course.id)

@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course

    # Enroll check
    if not Enrollment.objects.filter(
        user=request.user,
        course=course,
        paid=True
    ).exists():
        return redirect("course_detail", course.id)

    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    progress.completed = True
    progress.save()

    # Redirect to next lesson if exists
    lessons = list(Lesson.objects.filter(
        section__course=course
    ).order_by("id"))

    index = lessons.index(lesson)

    if index + 1 < len(lessons):
        return redirect("lesson", lessons[index + 1].id)

    # All lessons completed
    return redirect("certificate", course.id)

from .models import CourseReview

@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Progress check
    total = Lesson.objects.filter(section__course=course).count()
    completed = LessonProgress.objects.filter(
        user=request.user,
        lesson__section__course=course,
        completed=True
    ).count()

    if total == 0 or completed < total:
        return redirect("course_detail", course.id)

    # Prevent duplicate review
    if CourseReview.objects.filter(course=course, user=request.user).exists():
        return redirect("course_detail", course.id)

    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment")

        CourseReview.objects.create(
            course=course,
            user=request.user,
            rating=rating,
            comment=comment
        )

    return redirect("course_detail", course.id)
