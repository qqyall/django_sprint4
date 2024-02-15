from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),

    path('posts/create',
         views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(), name='post_detail'),
    path(
        'posts/<int:pk>/edit/',
        views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),

    path('posts/<int:post_id>/comments/',
         views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment'),

    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(), name='category_posts'),

    path('profile/edit_profile/', views.edit_profile, name='edit_profile'),
    path('profile/<slug:username>/', views.profile, name='profile'),

    path('auth/', include('django.contrib.auth.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
