from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from polls.models import Question, Choice, Vote

from commons.constants import Messages


class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    choices = serializers.StringRelatedField(many=True, label='选项')

    class Meta:
        model = Question
        fields = ['url', 'owner', 'title', 'created', 'choices']


class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = ['url', 'title', 'question']

    def validate(self, attrs):
        question = attrs['question']
        request = self.context['request']
        if question.owner != request.user:
            raise ValidationError({'question': Messages.QUESTION_NOT_ALLOWED})

        return attrs


class VoteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    question = serializers.ReadOnlyField(source='choice.question.title')

    class Meta:
        model = Vote
        fields = ['url', 'user', 'question']
