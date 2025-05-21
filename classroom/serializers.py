
from rest_framework import serializers
from .models import Block, Classroom

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'name']

class ClassroomSerializer(serializers.ModelSerializer):
    block = BlockSerializer(read_only=True)

    class Meta:
        model = Classroom
        fields = ['id', 'name', 'block', 'capacity', 'status']