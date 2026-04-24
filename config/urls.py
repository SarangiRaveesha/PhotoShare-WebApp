from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from photos import views as photo_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', photo_views.user_logout, name='logout'),
    path('', include('photos.urls')),
    path('users/', include('users.urls')),

    path('login/', user_views.user_login, name='login'),
    path('logout/', user_views.user_logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
