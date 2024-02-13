from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import (
    get_list_or_404, get_object_or_404, render, redirect
)
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth import get_user_model

from .models import Category, Post, Comment

from .forms import PostForm, CommentForm
from users.forms import CustomUserChangeForm


def post_published_filter():
    return Post.objects.all().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.utcnow()
    )


class PostListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10
    template_name = 'blog/index.html'
    ordering = ('-pub_date',)


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('blog:index')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('post')
        )
        return context


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostDeleteView(DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


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


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(request.POST or None, instance=comment)
    context = {'comment': form}
    if form.is_valid():
        form = form.save()
    template = 'blog/comment.html'
    return render(request, template, context)


def delete_comment(request, pk):
    pass


@login_required
def profile(request, username):
    profile = get_object_or_404(
        get_user_model().objects.all().filter(username=username)
    )
    page_obj = get_list_or_404(
        Post.objects.filter(author_id=request.user.id)
    )
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
