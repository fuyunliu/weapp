from rest_framework import routers
from collects import views

router = routers.DefaultRouter()
router.register('collects', views.CollectViewSet, 'collect')
router.register('collections', views.CollectionViewSet, 'collection')
urlpatterns = router.urls
