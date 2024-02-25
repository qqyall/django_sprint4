from .forms import PostForm
from .models import Post


class PostMixin:
    model = Post
    form_class = PostForm
