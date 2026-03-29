from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserEditForm

User = get_user_model()

def get_post_queryset():
    """Возвращает queryset с опубликованными постами"""
    return Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related(
        'author', 'location', 'category'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def index(request):
    post_list = get_post_queryset()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)



def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_post_queryset().filter(category=category)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        get_post_queryset() | Post.objects.filter(author=request.user if request.user.is_authenticated else None),
        id=post_id
    )
    comments = post.comments.select_related('author')
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)

    # все посты автора
    posts = Post.objects.filter(author=author).select_related(
        'category', 'location'
    ).annotate(
        comment_count=Count('comments')
    )

    # если пользователь не автор — показываем только опубликованное
    if request.user != author:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    # сортировка после всех фильтров для пагинации
    posts = posts.order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': author,
        'page_obj': page_obj,
        'is_owner': request.user == author,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = UserEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", request.user.username)
    return render(request, "blog/user.html", {"form": form})


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    context = {'form': post}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration_form.html', {'form': form})
