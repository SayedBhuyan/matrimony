from django.urls import path
from . import views

app_name = 'discovery'

urlpatterns = [
    path('matches/', views.matches_view, name='matches'),
    path('search/', views.search_view, name='search'),
]
