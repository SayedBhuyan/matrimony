from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('setup/', views.profile_setup, name='profile_setup'),
    path('me/', views.my_profile, name='my_profile'),
    path('edit/', views.profile_edit, name='profile_edit_default'),
    path('edit/<str:section>/', views.profile_edit, name='profile_edit'),
    path('photos/upload/', views.photo_upload, name='photo_upload'),
    path('photos/<uuid:photo_id>/delete/', views.photo_delete, name='photo_delete'),
    path('photos/<uuid:photo_id>/set-primary/', views.photo_set_primary, name='photo_set_primary'),
    path('<uuid:profile_id>/', views.profile_detail, name='profile_detail'),
]
