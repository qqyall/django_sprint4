from .models import Post
from .forms import PostForm


class PostMixin:
    model = Post
    form_class = PostForm
