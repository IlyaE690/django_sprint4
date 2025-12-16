from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserProfileForm, UserRegistrationForm

User = get_user_model()


def get_published_posts(user=None):
    posts = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        category__is_published=True,
    )

    if not user or not user.is_authenticated:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )
    else:
        posts = posts.filter(
            Q(is_published=True, pub_date__lte=timezone.now()) |
            Q(author=user)
        )

    return posts


def index(request):
    post_list = get_published_posts(request.user)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location')
        .prefetch_related('comments__author'),
        id=id
    )

    if not post.is_published or post.pub_date > timezone.now():
        if not request.user.is_authenticated or request.user != post.author:
            return redirect('blog:index')

    comments = post.comments.all()
    comment_form = CommentForm()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', id=post.id)

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = category.category_posts.filter(
        Q(is_published=True, pub_date__lte=timezone.now()) |
        Q(author=request.user) if request.user.is_authenticated else Q()
    ).select_related('author', 'location')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'category': category
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)

    if request.user == user:
        post_list = user.posts.select_related('category', 'location').all()
    else:
        post_list = user.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).select_related('category', 'location')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})


class RegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', id=post.id)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.id})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    context_object_name = 'form'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    context_object_name = 'comment'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.post.id})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    context_object_name = 'comment'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.post.id})


def about(request):
    return render(request, 'pages/about.html')


def rules(request):
    return render(request, 'pages/rules.html')


def csrf_failure(request, reason=""):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)