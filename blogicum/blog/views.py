from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserCreateForm, UserEditForm
from .models import Category, Comment, Post


POSTS_PER_PAGE = 10
User = get_user_model()


def Published_Queryset():
    return (
        Post.objects.select_related("author", "category", "location")
        .annotate(comment_count=Count("comments"))
        .filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
        .order_by("-pub_date")
    )


def Paginate(request, queryset):
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def get_Post_for(post_id, user):
    post = get_object_or_404(
        Post.objects.select_related("author", "category", "location")
        .annotate(comment_count=Count("comments")),
        pk=post_id,
    )
    if post.author == user:
        return post
    if (
        post.is_published
        and post.category
        and post.category.is_published
        and post.pub_date <= timezone.now()
    ):
        return post
    raise Http404


def index(request):
    page_obj = Paginate(request, Published_Queryset())
    return render(request, "blog/index.html", {"page_obj": page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    page_obj = Paginate(
        request,
        Published_Queryset().filter(category=category),
    )
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj},
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        "author",
        "category",
        "location",
    ).annotate(comment_count=Count("comments")).filter(author=profile_user)
    if request.user != profile_user:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    page_obj = Paginate(request, posts.order_by("-pub_date"))
    context = {
        "profile": profile_user,
        "page_obj": page_obj,
    }
    return render(request, "blog/profile.html", context)


def post_detail(request, post_id):
    post = get_Post_for(post_id, request.user)
    comments = post.comments.select_related("author").order_by("created_at")
    comment_form = CommentForm() if request.user.is_authenticated else None
    context = {
        "post": post,
        "comments": comments,
        "form": comment_form,
    }
    return render(request, "blog/detail.html", context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", request.user.username)
    return render(request, "blog/create.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)
    return render(request, "blog/create.html", {"form": form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    form = PostForm(instance=post)
    if request.method == "POST":
        post.delete()
        return redirect("blog:index")
    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    post = get_Post_for(post_id, request.user)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("blog:post_detail", post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)
    return render(
        request,
        "blog/comment.html",
        {"form": form, "comment": comment, "post": post},
    )


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)
    return render(
        request,
        "blog/comment.html",
        {"comment": comment, "post": post},
    )


@login_required
def edit_profile(request):
    form = UserEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", request.user.username)
    return render(request, "blog/user.html", {"form": form})


def registration(request):
    form = UserCreateForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("blog:index")
    return render(request, "registration/registration_form.html", {"form": form})
