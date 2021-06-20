from rest_framework import routers
from taggit import views

router = routers.DefaultRouter()
router.register('tags', views.TagViewSet, 'tag')
router.register('tagged-items', views.TaggedItemViewSet, 'tagged_items')
urlpatterns = router.urls
