from django.conf import settings

from django.urls import path, include
from rest_framework import routers

from likes import views as likes_views
from follows import views as follows_views
from comments import views as comments_views
from collects import views as collects_views

router = routers.DefaultRouter()
router.register('likes', likes_views.LikeViewSet, 'like')
router.register('follows', follows_views.FollowViewSet, 'follow')
router.register('comments', comments_views.CommentViewSet, 'comment')
router.register('collects', collects_views.CollectViewSet, 'collect')
router.register('collections', collects_views.CollectionViewSet, 'collection')

urlpatterns = [
    path('oauth/', include('oauth.urls')),
    path('weblog/', include('weblog.urls')),
    path('wechat/', include('wechat.urls')),
    path('poetry/', include('poetry.urls')),
    path('polls/', include('polls.urls')),
    path('actions/', include(router.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    from django.contrib import admin
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

    urlpatterns += [
        path('admin/', admin.site.urls),

        # Django Debug Tools
        path('__debug__/', include(debug_toolbar.urls)),

        # Browsable API Login
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

        # Your Patterns
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

        # Optional UI:
        path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
