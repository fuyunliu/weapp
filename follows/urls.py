from rest_framework import routers
from follows import views

router = routers.DefaultRouter()
router.register('follows', views.FollowViewSet, 'follow')
urlpatterns = router.urls
