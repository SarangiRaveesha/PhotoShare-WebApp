from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/open/<int:notification_id>/', views.open_notification, name='open_notification'),
    path('delete-account/', views.delete_account, name='delete_account'),

    path('<str:username>/add-friend/', views.send_friend_request, name='send_friend_request'),
    path('<str:username>/accept-friend/', views.accept_friend_request, name='accept_friend_request'),
    path('<str:username>/remove-friend/', views.remove_friend, name='remove_friend'),
    path('<str:username>/', views.profile, name='profile'),
]