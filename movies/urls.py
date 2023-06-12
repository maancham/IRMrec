from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("home/", views.home, name="home"),
    path("items/", views.movie_list, name="movie_list"),
    path("item/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("judge/", views.judge, name="movie_judge"),
    path("ranking/", views.final_ranking, name="final_ranking"),
]
