from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/cinema/", include("airport.urls", namespace="airport")),
    # path("api/user/", include("user.urls", namespace="user")),
]
