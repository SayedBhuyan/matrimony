from django.urls import path
from . import views

app_name = 'connections'

urlpatterns = [
    # Interest endpoints
    path('interest/send/<uuid:profile_id>/', views.send_interest, name='send_interest'),
    path('interest/accept/<uuid:interest_id>/', views.accept_interest, name='accept_interest'),
    path('interest/reject/<uuid:interest_id>/', views.reject_interest, name='reject_interest'),
    path('interest/cancel/<uuid:interest_id>/', views.cancel_interest, name='cancel_interest'),
    path('interests/received/', views.received_interests, name='received_interests'),
    path('interests/sent/', views.sent_interests, name='sent_interests'),
    
    # Favorite endpoints
    path('favorite/add/<uuid:profile_id>/', views.add_favorite, name='add_favorite'),
    path('favorite/remove/<uuid:profile_id>/', views.remove_favorite, name='remove_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),

    # Trust & safety endpoints
    path('block/<uuid:user_id>/', views.block_user, name='block_user'),
    path('block/<uuid:user_id>/unblock/', views.unblock_user, name='unblock_user'),
    path('blocked/', views.blocked_users, name='blocked_users'),
    path('report/<uuid:user_id>/', views.report_user, name='report_user'),
]
