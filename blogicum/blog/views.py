from datetime import datetime

from django.shortcuts import get_list_or_404, get_object_or_404, render

from .consts import NUMBER_OF_POSTS_ON_MAIN_PAGE
from .models import Category, Post


def post_published_filter():
    return Post.objects.all().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.utcnow()
    )


def index(request):
    template = 'blog/index.html'
    post_list = post_published_filter(
    ).order_by('-created_at')[:NUMBER_OF_POSTS_ON_MAIN_PAGE]

    context = {
        'post_list': post_list
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        post_published_filter(),
        pk=post_id
    )

    context = {
        'post': post
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    post_list = get_list_or_404(
        post_published_filter(),
        category__slug=category_slug
    )

    category = get_object_or_404(
        Category.objects.filter(
            slug=category_slug
        )
    )

    context = {'post_list': post_list, 'category': category}
    return render(request, template, context)
