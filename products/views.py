from rest_framework import viewsets, generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.db.models import Avg
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import get_object_or_404, render, redirect
from products.models import Product
from reviews.models import Review
from products.serializers import ProductSerializer, ReviewSerializer, RegisterSerializer
from products.permissions import IsAdminOrReadOnly, IsRegularUser
from django.contrib.auth.models import User

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Product objects.
    - Admins can create, update, delete products
    - All users can view products
    """
    queryset = Product.objects.all().annotate(average_rating=Avg('reviews__rating'))
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Review objects.
    - Regular users can create reviews
    - All users can view reviews
    - Prevents duplicate reviews from the same user for the same product
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsRegularUser]

    def get_queryset(self):
        """Filter reviews by product if product ID is provided in query params"""
        product_id = self.request.query_params.get('product')
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return super().get_queryset()

    def perform_create(self, serializer):
        """Automatically associate review with authenticated user"""
        serializer.save(user=self.request.user)

class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    Creates a new user and generates an authentication token.
    """
    queryset = User.objects.all()  
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        """Handle user registration and token creation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create or get authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "user": serializer.data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)

class AddProductReview(LoginRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'reviews/form.html', {'product': product})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if request.user.is_staff:
            return redirect('product_detail', pk=product.pk)

        if Review.objects.filter(user=request.user, product=product).exists():
            return redirect('product_detail', pk=product.pk)

        rating = int(request.POST.get('rating'))
        feedback = request.POST.get('feedback')
        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            feedback=feedback
        )
        return redirect('product_detail', pk=product.pk)