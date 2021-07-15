from rest_framework import routers
from weblog import views

router = routers.DefaultRouter()
router.register('articles', views.ArticleViewSet, 'article')
router.register('pins', views.PinViewSet, 'pin')
router.register('categories', views.CategoryViewSet, 'category')
router.register('topics', views.TopicViewSet, 'topic')
urlpatterns = router.urls
