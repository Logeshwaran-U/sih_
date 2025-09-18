from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name="index"),
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login_page'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('state/<slug:slug>/', views.state_details, name="state_details"),

    # new
    path('state/<int:state_id>/add-festival/', views.add_festival, name="add_festival"),
    path('state/<int:state_id>/add-music/', views.add_music, name="add_music"),

    path('music/<int:pk>/update/', views.update_music, name='update_music'),
    path('festival/<int:pk>/update/', views.update_festival, name='update_festival'),

    
    path('community/global/', views.community_global, name='community_global'),
    path('community/<int:pk>/update/', views.update_global_post, name='update_global_post'),

    path('community/add/', views.add_global_post, name='add_global_post'),

    # State-specific Community
    path('state/<slug:slug>/community/add/', views.add_state_post, name='add_state_post'),
    #path

    
    path("api/generate/", views.generate_story, name="generate_story"),
    path("api/result/<str:task_id>/", views.get_story_result, name="get_story_result"),
    path("story/", views.story_page, name="story_page"),
    path("image-upload/", views.image_to_culture, name="image_upload"),
    path("image-result/<str:task_id>/", views.get_image_culture_result, name="image_result"),
    path("generate-story/", views.generate_culture_story, name="generate_story"),
    path("story-result/<str:task_id>/", views.get_culture_story_result, name="story_result"),
      # page (frontend)
    path("generate-3d/", views.generate_3d_page, name="generate_3d_page"),

    # api (POST only)
    path("api/generate-3d/", views.generate_3d_model_view, name="generate_3d_api"),

]


