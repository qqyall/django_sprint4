from django.core.paginator import Paginator
from .consts import POSTS_ON_PAGE
from .models import Post
from django.db.models import Count


def wrap_paginator_commentcounter(self, filter_func, **kwargs):
    def wrapper(self):
        paginator = Paginator(
            filter_func(**kwargs),
            POSTS_ON_PAGE
        )
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        for obj in page_obj:
            obj.comment_count = Post.objects.filter(
                pk=obj.id).annotate(Count('comments'))[0].comments__count

        return page_obj
    return wrapper(self)
