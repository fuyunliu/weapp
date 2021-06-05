from rest_framework import serializers

from wechat.models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = ['url', 'sender', 'reciever', 'created', 'body']

    def create(self, validated_data):
        message = Message.objects.create(**validated_data)
        return message
