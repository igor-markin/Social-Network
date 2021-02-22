from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))

    context = {
        'page': page,
        'paginator': paginator,
        'index': True,
    }

    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))

    context = {
        'group': group,
        'page': page,
        'paginator': paginator,
    }

    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')

    return render(request, 'new_post.html', {'form': form, })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }

    return render(request, 'new_post.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))

    is_follow = (
            request.user.is_authenticated and
            request.user != user and
            user.following.filter(user=request.user, author=user).exists()
    )

    context = {
        'page': page,
        'paginator': paginator,
        'author': user,
        'is_follow': is_follow,
    }

    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)

    context = {
        'post': post,
        'author': post.author,
        'comments': post.comments.all(),
        'form': CommentForm(),
    }

    return render(request, 'post.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))

    context = {
        'page': page,
        'paginator': paginator,
    }

    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('profile', username=username)
    Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(Follow, user=request.user,
                               author__username=username)
    follow.delete()

    return redirect('profile', username=username)


def page_not_found(request, exception):  # noqa
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
