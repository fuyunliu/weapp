from django.urls import path
from rest_framework import routers
from oauth import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, 'user')
router.register('profiles', views.ProfileViewSet, 'profile')
router.register('groups', views.GroupViewSet, 'group')
urlpatterns = router.urls
urlpatterns += [
    path('token/', views.TokenView.as_view(), name='token'),
    path('captcha/', views.CaptchaView.as_view(), name='captcha')
]
