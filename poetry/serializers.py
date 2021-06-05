from rest_framework import serializers
from poetry.models import Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['url', 'name', 'dynasty', 'desc']
