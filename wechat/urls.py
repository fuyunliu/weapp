from rest_framework import routers
from wechat import views

router = routers.DefaultRouter()
router.register('messages', views.MessageViewSet, 'message')
urlpatterns = router.urls
