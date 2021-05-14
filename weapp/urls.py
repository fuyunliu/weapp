from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('oauth/', include('oauth.urls')),
    path('weblog/', include('weblog.urls')),
    path('actions/', include('likes.urls')),
    path('actions/', include('follows.urls')),
    path('actions/', include('comments.urls')),
    path('admin/', admin.site.urls),
]
