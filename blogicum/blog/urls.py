from django.urls import path, include
from . import views
from .views import (PostCreateView, PostUpdateView, PostDeleteView,
                    CommentUpdateView, CommentDeleteView, RegistrationView)

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('posts/<int:post_id>/comment/', views.post_detail, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:pk>/',
         CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:pk>/',
         CommentDeleteView.as_view(), name='delete_comment'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', RegistrationView.as_view(), name='registration'),

    path('pages/about/', views.about, name='about'),
    path('pages/rules/', views.rules, name='rules'),
]