from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from products.models import Product
from reviews.models import Review
from django import forms
from django.db.models import Avg
from django.views.generic import RedirectView
from django.contrib.auth.forms import UserCreationForm

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']
@login_required
def product_list(request):
    products = Product.objects.annotate(average_rating=Avg('reviews__rating'))
    return render(request, 'products/list.html', {'products': products})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    can_review = False
    if request.user.is_authenticated and not request.user.is_staff:
        if not Review.objects.filter(user=request.user, product=product).exists():
            can_review = True
    return render(request, 'products/detail.html', {
        'product': product, 'reviews': reviews,
        'average_rating': average_rating, 'can_review': can_review
    })

@user_passes_test(lambda u: u.is_staff)
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/form.html', {'form': form, 'title': 'Add Product'})

@user_passes_test(lambda u: u.is_staff)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/form.html', {'form': form, 'title': 'Edit Product'})

@user_passes_test(lambda u: u.is_staff)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'products/confirm_delete.html', {'product': product})

@login_required
def add_product_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_staff:
        return redirect('product_detail', pk=product_id)

    if Review.objects.filter(user=request.user, product=product).exists():
        return redirect('product_detail', pk=product_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        feedback = request.POST.get('feedback')
        if rating < 1 or rating > 5:
            return render(request, 'reviews/form.html', {'product': product, 'error': 'Invalid rating'})
        if not feedback:
            return render(request, 'reviews/form.html', {'product': product, 'error': 'Please enter feedback'})
        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            feedback=feedback
        )
        return redirect('product_detail', pk=product_id)

    return render(request, 'reviews/form.html', {'product': product})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                return render(request, 'registration/register.html', {'form': form, 'error': 'Username already exists'})
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def product_list(request):
    products = Product.objects.annotate(average_rating=Avg('reviews__rating'))
    for product in products:
        if product.reviews.count() == 0:
            product.average_rating = None
    return render(request, 'products/list.html', {'products': products})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    if reviews.count() == 0:
        average_rating = None
    else:
        average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    can_review = False
    if request.user.is_authenticated and not request.user.is_staff:
        if not Review.objects.filter(user=request.user, product=product).exists():
            can_review = True
    return render(request, 'products/detail.html', {
        'product': product, 'reviews': reviews,
        'average_rating': average_rating, 'can_review': can_review
    })