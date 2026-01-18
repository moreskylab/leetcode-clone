from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'bio', 'avatar', 'solved_count', 'points', 'created_at')
        read_only_fields = ('id', 'solved_count', 'points', 'created_at')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with additional statistics"""
    
    total_submissions = serializers.SerializerMethodField()
    acceptance_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'bio', 'avatar', 'solved_count', 'points', 'created_at',
                  'total_submissions', 'acceptance_rate')
        read_only_fields = ('id', 'username', 'email', 'solved_count', 
                            'points', 'created_at')
    
    def get_total_submissions(self, obj):
        return obj.submissions.count()
    
    def get_acceptance_rate(self, obj):
        total = obj.submissions.count()
        if total == 0:
            return 0
        accepted = obj.submissions.filter(status='Accepted').count()
        return round((accepted / total) * 100, 2)


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for leaderboard display"""
    
    rank = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar', 'solved_count', 'points', 'rank')
