from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from users.forms import CustomUserChangeForm

from .consts import POSTS_ON_PAGE
from .forms import CommentForm, ProfileForm
from .models import Category, Comment, Post
from .decorators import wrap_paginator_commentcounter
from .mixins import PostMixin


def post_published_filter():
    return Post.objects.all().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=timezone.now()
    ).select_related('author', 'location', 'category')


class PostListView(PostMixin, ListView):
    template_name = 'blog/index.html'
    ordering = ('-pub_date',)
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = wrap_paginator_commentcounter(
            self, post_published_filter,)
        return context


class PostCreateView(PostMixin, CreateView):
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.success_url = reverse_lazy(
            'blog:profile', args=[self.request.user])
        return super().form_valid(form)


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        instance = self.get_object()

        def instance_not_published(instance):
            return (
                not instance.is_published
                or not instance.category.is_published
                or instance.pub_date > timezone.now()
            )

        if instance_not_published(instance):
            if instance.author_id != instance.author:
                raise Http404

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['post_id'])
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('post')
        )
        return context


class PostUpdateView(PostMixin, UpdateView):
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != self.request.user:
            if self.request.user.pk is None:
                return redirect('login')
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(PostMixin, DeleteView):
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != self.request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    ordering = ('-id',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.filter(is_published=1)
            .filter(slug=self.kwargs['category_slug'])
        )
        paginator = Paginator(
            post_published_filter().filter(
                category__slug=self.kwargs['category_slug']
            ), POSTS_ON_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        get_object_or_404(Comment, pk=self.kwargs['comment_id'],
                          author=self.request.user)
        post_id = self.request.path.split('/')[-4]
        self.success_url = reverse_lazy('blog:post_detail', args=[post_id])
        return super().form_valid(form)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id, author=request.user)
    if request.method == 'POST':
        instance.delete()

        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html')


class ProfileDetailView(DetailView):
    model = get_user_model()
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            get_user_model().objects.all().filter(username=kwargs['object'])
        )
        context['profile'] = profile
        context['form'] = ProfileForm()

        context['page_obj'] = wrap_paginator_commentcounter(
            self, Post.objects.filter, author_id=profile.id)
        return context

    def get_queryset(self):
        return super().get_queryset()


@login_required
def edit_profile(request):
    form = CustomUserChangeForm(request.POST, instance=request.user)
    context = {'form': form}
    if form.is_valid():
        form.save()
    template = 'blog/user.html'
    return render(request, template, context)
