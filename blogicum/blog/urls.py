from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),

    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),

    path('create_post/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),

    path('profile/edit_profile/',
         views.edit_profile, name='edit_profile'),
    path('profile/<slug:username>/', views.profile, name='profile'),
]
