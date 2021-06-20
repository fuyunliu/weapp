from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from polls.models import Question, Choice, Vote

from commons.constants import Messages


class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    choices = serializers.StringRelatedField(many=True, label='选项')

    class Meta:
        model = Question
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = '__all__'

    def validate(self, attrs):
        question = attrs.get('question')
        request = self.context['request']
        if question is not None and question.owner != request.user:
            raise ValidationError({'question': Messages.QUESTION_NOT_ALLOWED})

        return attrs


class VoteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    question = serializers.ReadOnlyField(source='choice.question.title')

    class Meta:
        model = Vote
        fields = '__all__'

    def validate(self, attrs):
        choice = attrs['choice']
        request = self.context['request']
        vote_count = Vote.objects.filter(user=request.user, choice__question=choice.question).count()
        if vote_count >= choice.question.max_choices:
            raise ValidationError(Messages.VOTE_MAX_NUM.format(choice.question.max_choices))

        return attrs

    def create(self, validated_data):
        vote, _ = Vote.objects.get_or_create(**validated_data)
        return vote
