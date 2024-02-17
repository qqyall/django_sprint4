from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import make_aware
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from users.forms import CustomUserChangeForm

from .consts import POSTS_ON_PAGE
from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


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

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])

        def instance_not_published(instance):
            return (
                not instance.is_published
                or not instance.category.is_published
                or instance.pub_date > make_aware(datetime.utcnow())
            )

        if instance_not_published(instance):
            if instance.author_id != request.user.pk:
                raise Http404
        return super().dispatch(request, *args, **kwargs)

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
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != self.request.user:
            if self.request.user.pk is None:
                return redirect('login')
            return redirect('blog:post_detail', kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != self.request.user:
            return redirect('blog:post_detail', kwargs['pk'])
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

        # Update comment count on post
        post = Post.objects.get(pk=post_id)
        post.comment_count += 1
        post.save(update_fields=['comment_count'])
    return redirect('blog:post_detail', pk=post_id)


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'id'
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        get_object_or_404(Comment, pk=self.kwargs['id'],
                          author=self.request.user)
        post_id = self.request.path.split('/')[-4]
        self.success_url = reverse_lazy('blog:post_detail', args=[post_id])
        return super().form_valid(form)


@login_required
def delete_comment(request, post_id, id):
    instance = get_object_or_404(Comment, pk=id, author=request.user)
    if request.method == 'POST':
        instance.delete()
        # Update comment count on post
        post = Post.objects.get(pk=post_id)
        post.comment_count -= 1
        post.save(update_fields=['comment_count'])
        return redirect('blog:post_detail', pk=post_id)
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
        paginator = Paginator(
            Post.objects.filter(author_id=profile.id), POSTS_ON_PAGE)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


@login_required
def edit_profile(request):
    instance = get_object_or_404(get_user_model(), username=request.user)
    form = CustomUserChangeForm(request.POST, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    template = 'blog/user.html'
    return render(request, template, context)
