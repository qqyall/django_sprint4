from datetime import datetime

from django.shortcuts import (
    get_list_or_404, get_object_or_404, render, _get_queryset)
from django.contrib.auth import get_user_model

from .consts import NUMBER_OF_POSTS_ON_MAIN_PAGE
from .models import Category, Post
from .forms import PostForm

from users.forms import CustomUserChangeForm


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
        'page_obj': post_list
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        post_published_filter(),
        pk=post_id
    )
    context = {'post': post}
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


def create_post(request):
    template = 'blog/create.html'
    form = PostForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, template, context)


def profile(request, username):
    profile = get_object_or_404(
        get_user_model().objects.all().filter(username=username)
    )
    posts = _get_queryset(Post.objects.all().filter(author=profile.id)) | None
    # posts = get_list_or_404(
    #     Post.objects.all().filter(author=profile.id)
    # ) | None
    template = 'blog/profile.html'
    context = {'profile': profile, 'page_obj': posts}
    return render(request, template, context=context)


def edit_profile(request, username=None):
    instance = get_object_or_404(get_user_model(), username=request.user)
    form = CustomUserChangeForm(request.POST, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    template = 'blog/user.html'
    return render(request, template, context)
