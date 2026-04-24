from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    #Upload Photo
    path('upload/', views.upload_photo, name='upload'),
    path('edit/<int:photo_id>/', views.edit_photo, name='edit_photo'),
    path('delete/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('like/<int:photo_id>/', views.toggle_like, name='like'),
    path('comment/<int:photo_id>/', views.add_comment, name='comment'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('react/<int:comment_id>/<str:emoji>/', views.react_comment, name='react'),
    path('mention-suggestions/', views.mention_suggestions, name='mention_suggestions'),
    path('logout/', views.user_logout, name='logout'),
]
