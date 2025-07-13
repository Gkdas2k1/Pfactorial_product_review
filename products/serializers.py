from rest_framework import serializers
from django.db.models import Avg, Count
from django.contrib.auth.models import User
from products.models import Product
from reviews.models import Review

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model with aggregated review data"""
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'average_rating', 'review_count']
        read_only_fields = ['id', 'average_rating', 'review_count']

    def get_average_rating(self, obj):
        """Get average rating from annotated queryset or calculate if needed"""
        if hasattr(obj, 'average_rating'):
            return round(obj.average_rating, 1) if obj.average_rating else None
        rating = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(rating, 1) if rating else None

    def get_review_count(self, obj):
        """Get review count from annotated queryset or calculate if needed"""
        if hasattr(obj, 'review_count'):
            return obj.review_count
        return obj.reviews.count() if obj.reviews else 0

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model with validation"""
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'feedback', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, data):
        """Validate that a user can only review a product once"""
        user = self.context['request'].user
        
        # Ensure product is provided
        if 'product' not in data:
            raise serializers.ValidationError({
                'product': 'Product is required for review submission'
            })
        
        product = data['product']
        
        # Check for existing review
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError({
                'non_field_errors': ['You have already reviewed this product.']
            })
        
        return data

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'min_length': 'Password must be at least 8 characters long'
        }
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'username': {'required': True},
            'password': {'required': True}
        }

    def create(self, validated_data):
        """Create a new user with encrypted password"""
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

    def to_representation(self, instance):
        """Override to avoid returning password hash"""
        data = super().to_representation(instance)
        data.pop('password', None)
        return data