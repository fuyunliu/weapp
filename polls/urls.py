from rest_framework import routers
from polls import views

router = routers.DefaultRouter()
router.register('questions', views.QuestionViewSet, 'question')
router.register('choices', views.ChoiceViewSet, 'choice')
router.register('votes', views.VoteViewSet, 'vote')
urlpatterns = router.urls
