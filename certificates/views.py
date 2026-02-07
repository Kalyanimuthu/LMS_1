from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from courses.models import Course, Lesson, LessonProgress



@login_required
def certificate_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    total_lessons = Lesson.objects.filter(
        section__course=course
    ).count()

    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__section__course=course,
        completed=True
    ).count()

    # SAFETY CHECK
    if total_lessons == 0:
        progress = 0
    else:
        progress = int((completed_lessons / total_lessons) * 100)

    # 🔒 LOCK ONLY CERTIFICATE PAGE
    if progress < 100:
        return render(request, "certificates/locked.html", {
            "course": course,
            "progress": progress
        })

    # 🔓 UNLOCK CERTIFICATE
    return render(request, "certificates/unlocked.html", {
        "course": course
    })

@login_required
def download_certificate(request, course_id):
    course = Course.objects.get(id=course_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=certificate.pdf"

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Border
    pdf.setStrokeColorRGB(0.48, 0.17, 0.17)
    pdf.setLineWidth(4)
    pdf.rect(30, 30, width - 60, height - 60)

    # Title
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width / 2, height - 120, "Certificate of Completion")

    # Subtitle
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 170, "This is proudly presented to")

    # User Name
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(
        width / 2,
        height - 220,
        request.user.get_full_name() or request.user.username
    )

    # Course Text
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        width / 2,
        height - 270,
        "for successfully completing the course"
    )

    # Course Title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(width / 2, height - 310, course.title)

    # Footer
    pdf.setFont("Helvetica", 12)
    pdf.drawString(80, 120, "Authorized by: LMS Platform")
    pdf.drawRightString(width - 80, 120, "Date: __________")

    pdf.showPage()
    pdf.save()

    return response
