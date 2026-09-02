from django.urls import path

from . import views

app_name = 'messaging'

urlpatterns = [
    path('conversations/', views.conversations, name='conversations'),
    path('conversation/<uuid:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<uuid:conversation_id>/send/', views.send_message, name='send_message'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]
