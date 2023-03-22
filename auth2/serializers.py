from rest_framework import serializers
from auth2.models import User 


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            fullname=validated_data['fullname'],
            password=validated_data['password'],
        )
        return user
    
    class Meta():
        model = User
        fields = ('id', 'username', 'fullname', 'email', 'password')


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    
    class Meta():
        model = User
        fields = ('email', 'password')


class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ('id','email','fullname','username','company')


class ChangePermissionSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ('id', 'company')

    def update(self, instance, validated_data): 
        instance.company = validated_data.get('company', instance.company)
        instance.save()
        return instance