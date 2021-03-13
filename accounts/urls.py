from django.urls import path, include
from rest_framework import routers
from accounts import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)
urlpatterns = router.urls
