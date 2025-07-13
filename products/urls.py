from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet, ReviewViewSet, RegisterView
from .views_api import RegisterAPIView
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('<int:pk>/review/', views.AddProductReview.as_view(), name='add_product_review'),
]