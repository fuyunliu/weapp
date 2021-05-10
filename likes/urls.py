from rest_framework import routers
from likes import views

router = routers.DefaultRouter()
router.register('likes', views.LikeViewSet, 'like')
urlpatterns = router.urls
