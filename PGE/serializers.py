from django.contrib.auth.models import User

from rest_framework import serializers

from PGE.models import Employee, Link, Priority, Project, Role

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'email',)


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ('magnitude',)

class EmployeeSerializer(serializers.ModelSerializer):
    
    priority = PrioritySerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Employee
        fields = ('user', 'priority',)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('project_name',)


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ('link_name', 'url',)