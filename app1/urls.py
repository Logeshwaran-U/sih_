from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name="index"),
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login_page'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('state/<slug:slug>/', views.state_details, name="state_details"),
    path("music/add/", views.add_music, name="add_music"),
    path("festival/add/", views.add_festival, name="add_festival"),
]


