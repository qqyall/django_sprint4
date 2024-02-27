from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .consts import POSTS_ON_PAGE
from .forms import CommentForm
from .mixins import PostMixin, PostUpdateMixin
from .models import Category, Comment, Post
from users.forms import CustomUserChangeForm


def post_published_filter():
    return Post.objects.all().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=timezone.now()
    ).select_related('author', 'location', 'category')


def add_comment_count(queryset):
    return queryset.annotate(comment_count=Count('comments'))


class PostListView(PostMixin, ListView):
    template_name = 'blog/index.html'
    ordering = ('-pub_date',)
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        return add_comment_count(
            post_published_filter()
        ).order_by(*self.ordering)


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    template_name = 'blog/create.html'

    def get_success_url(self) -> str:
        return reverse('blog:profile', args=[self.request.user])

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        self.queryset = self.get_queryset().filter(
            pk=self.kwargs[self.pk_url_kwarg])
        try:
            post = self.queryset.get()
            if post.author == self.request.user:
                return post
            return self.queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lt=timezone.now()
            ).get()
        except self.queryset.model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostUpdateView(LoginRequiredMixin, PostMixin, PostUpdateMixin,
                     UpdateView):
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class PostDeleteView(LoginRequiredMixin, PostMixin, PostUpdateMixin,
                     DeleteView):
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class CategoryListView(ListView):
    template_name = 'blog/category.html'
    ordering = ('-pub_date',)
    paginate_by = POSTS_ON_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug']
        )
        return context

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return add_comment_count(
            Post.objects.all().filter(
                category=category,
            ).filter(
                is_published=True,
                category__is_published=True,
                pub_date__lt=timezone.now()
            ).select_related(
                'author', 'location', 'category'
            )
        ).order_by(*self.ordering)


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


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', args=[post_id])

    def form_valid(self, form):
        get_object_or_404(Comment, pk=self.kwargs['comment_id'],
                          author=self.request.user)
        return super().form_valid(form)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id, author=request.user)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html')


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_PAGE
    ordering = ('-pub_date',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            get_user_model().objects.all().filter(
                username=self.kwargs['username'])
        )
        return context

    def get_queryset(self):
        author = get_object_or_404(
            get_user_model(),
            username=self.kwargs['username']
        )

        authors_posts = add_comment_count(
            Post.objects.all().filter(
                author_id=author.id
            ).select_related(
                'author', 'location', 'category'
            )
        ).order_by(*self.ordering)

        if str(author.username) == str(self.request.user):
            return authors_posts
        return authors_posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=timezone.now()
        )


@login_required
def edit_profile(request):
    form = CustomUserChangeForm(request.POST, instance=request.user)
    context = {'form': form}
    if form.is_valid():
        form.save()
    template = 'blog/user.html'
    return render(request, template, context)
