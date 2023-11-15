"""
Urls for profile app
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

# pylint: disable=C0103
app_name = "user_profile"

urlpatterns = [
    path(
        "api/v1/profile/<int:pk>/", views.CreateProfile.as_view(), name="user_profile"
    ),
    path(
        "api/v1/social_account/<int:pk>/",
        views.CreateSocial.as_view(),
        name="social_account",
    ),
    path(
        "api/v1/ratings/<int:user_id>/", views.UserRatingView.as_view(), name="ratings"
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
