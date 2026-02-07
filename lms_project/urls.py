from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from courses.views import landing_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('courses/', include('courses.urls')),
    path('', include('accounts.urls')),
    path("payments/", include("payments.urls")),
    path("certificate/", include("certificates.urls")),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
