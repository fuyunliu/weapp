from django.urls import path, include
from rest_framework import routers
from oauth import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, 'user')
router.register('profiles', views.ProfileViewSet, 'profile')
router.register('groups', views.GroupViewSet, 'group')
urlpatterns = router.urls
urlpatterns += [
    path('token/', views.TokenAPIView.as_view(), name='token'),
    path('code/', views.PhoneCodeView.as_view(), name='code'),
    path('oauth/', include('rest_framework.urls', namespace='rest_framework')),
]
