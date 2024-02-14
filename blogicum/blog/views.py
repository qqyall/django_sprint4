from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from users.forms import CustomUserChangeForm

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


class PostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    ordering = ('-id',)


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


class CategoryListView(ListView):
    model = Category
    paginate_by = 1
    template_name = 'blog/category.html'
    ordering = ('-id',)

    @staticmethod
    def post_published_filter():
        return Post.objects.all().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=datetime.utcnow()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = get_list_or_404(
            self.post_published_filter(),
            category__slug=self.kwargs['category_slug']
        )
        context['category'] = get_object_or_404(
            Category.objects.filter(slug=self.kwargs['category_slug'])
        )
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


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/comment.html', context)


@login_required
def profile(request, username):
    profile = get_object_or_404(
        get_user_model().objects.all().filter(username=username)
    )
    page_obj = Post.objects.filter(author_id=profile.id)

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
