from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm
from products.models import Product


@login_required
def review_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if Review.objects.filter(product=product, user=request.user).exists():
        return redirect('product_detail', pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'product': product})