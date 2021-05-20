import debug_toolbar
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
    path('oauth/', include('oauth.urls')),
    path('weblog/', include('weblog.urls')),
    path('actions/', include('likes.urls')),
    path('actions/', include('follows.urls')),
    path('actions/', include('comments.urls')),
    path('actions/', include('collects.urls')),
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
