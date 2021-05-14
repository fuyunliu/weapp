from rest_framework import routers
from comments import views

router = routers.DefaultRouter()
router.register('comments', views.CommentViewSet, 'comment')
urlpatterns = router.urls
