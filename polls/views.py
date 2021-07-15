from rest_framework import mixins, viewsets

from commons.permissions import IsOwnerOrReadOnly
from polls.models import Question, Choice, Vote
from polls.serializers import QuestionSerializer, ChoiceSerializer, VoteSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().select_related('owner').prefetch_related('choices')
    serializer_class = QuestionSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all().select_related('question')
    serializer_class = ChoiceSerializer
    permission_classes = [IsOwnerOrReadOnly]


class VoteViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Vote.objects.all().select_related('user', 'choice__question')
    serializer_class = VoteSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
