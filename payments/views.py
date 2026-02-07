from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment

@login_required
def demo_payment(request, course_id):
    course = Course.objects.get(id=course_id)

    if request.method == "POST":
        Enrollment.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={"paid": True}
        )
        return redirect("continue_learning", course.id)

    return render(request, "payments/demo_payment.html", {
        "course": course
    })
