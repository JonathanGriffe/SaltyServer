from django.urls import path
from board import views
from . import views

urlpatterns = [
    path("status", views.StatusDetail.as_view()),
]
