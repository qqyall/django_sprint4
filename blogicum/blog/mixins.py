from django.shortcuts import redirect

from .forms import PostForm
from .models import Post


class PostMixin:
    model = Post
    form_class = PostForm


class PostUpdateMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
