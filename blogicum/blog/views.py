from datetime import datetime

from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import (get_object_or_404, redirect, render)
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from users.forms import CustomUserChangeForm

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

from .consts import POSTS_ON_PAGE


def post_published_filter():
    return Post.objects.all().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.utcnow()
    )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = ('-pub_date',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(
            post_published_filter(), POSTS_ON_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return context


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = 'blog:index'

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.success_url = reverse_lazy(
            'blog:profile', args=[self.request.user])
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['post'].comment_count = Comment.objects.filter(
            post_id=self.kwargs['pk'])
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('post')
        )
        return context


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = 'blog:index'


class PostDeleteView(DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = "blog:index"

    def form_valid(self, form):
        return super().form_valid(form)


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    ordering = ('-id',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.filter(slug=self.kwargs['category_slug'])
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

        # Update comment count on post
        post = Post.objects.get(pk=post_id)
        post.comment_count += 1
        post.save(update_fields=['comment_count'])
    return redirect('blog:post_detail', pk=post_id)


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.success_url = reverse_lazy('blog:post_detail', args=["ZALUPA"])
        return super().form_valid(form)

    

@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(instance=instance)
    context = {'comment': form}
    if request.method == 'POST':
        instance.delete()
        # Update comment count on post
        post = Post.objects.get(pk=post_id)
        post.comment_count -= 1
        post.save(update_fields=['comment_count'])

        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def profile(request, username):
    profile = get_object_or_404(
        get_user_model().objects.all().filter(username=username)
    )
    paginator = Paginator(
        Post.objects.filter(author_id=profile.id), POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'blog/profile.html'
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, template, context=context)


@login_required
def edit_profile(request):
    instance = get_object_or_404(get_user_model(), username=request.user)
    form = CustomUserChangeForm(request.POST, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    template = 'blog/user.html'
    return render(request, template, context)
