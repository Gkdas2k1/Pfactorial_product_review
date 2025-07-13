"""
URL configuration for productreview project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
""" 

from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from products.views_html import product_list, product_detail, product_add, product_edit, product_delete, register
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from products import views

def logout_view(request):
    logout(request)
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',register,name='register'),
    path('api/', include('products.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', RedirectView.as_view(url='/login/')),
    path('products/', include([
        path('', login_required(product_list), name='product_list'),
        path('<int:pk>/', login_required(product_detail), name='product_detail'),
        path('add/', login_required(product_add), name='product_add'),
        path('<int:pk>/edit/', login_required(product_edit), name='product_edit'),
        path('<int:pk>/delete/', login_required(product_delete), name='product_delete'),
    ])),
    path('products/<int:pk>/review/', views.AddProductReview.as_view(), name='review_add'),
]