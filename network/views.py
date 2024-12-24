from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseForbidden
import json

from .models import User, Post
from .forms import PostEditForm


def paginate_posts(posts, request, per_page=10):
    # Order posts by date (newest first)
    posts = posts.order_by('-date')
    paginator = Paginator(posts, per_page)
    page = request.GET.get('page')
    
    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)
    
    return posts_page


def index(request):
    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content", "").strip()
        if content:
            Post.objects.create(user=request.user, content=content)
    
    all_posts = Post.objects.all()
    page_obj = paginate_posts(all_posts, request)
    
    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))
    
    # Get all posts for this user
    user_posts = Post.objects.filter(user=profile_user)
    
    # Set up pagination
    page_obj = paginate_posts(user_posts, request)
    
    # Check if the current user is following the profile user
    is_following = False
    if request.user.is_authenticated:
        is_following = request.user.following.filter(id=profile_user.id).exists()
    
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "page_obj": page_obj,
        "is_following": is_following,
        "followers_count": profile_user.followers_count(),
        "following_count": profile_user.following_count()
    })


@login_required
def toggle_follow(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)
    
    data = json.loads(request.body)
    try:
        user_to_follow = User.objects.get(pk=data.get("user_id"))
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
    # Users can't follow themselves
    if request.user == user_to_follow:
        return JsonResponse({"error": "Can't follow yourself"}, status=400)
    
    if request.user.following.filter(id=user_to_follow.id).exists():
        request.user.following.remove(user_to_follow)
        is_following = False
    else:
        request.user.following.add(user_to_follow)
        is_following = True
    
    return JsonResponse({
        "is_following": is_following,
        "followers_count": user_to_follow.followers_count()
    })


@login_required
def following(request):
    following_users = request.user.following.all()
    posts = Post.objects.filter(user__in=following_users)
    page_obj = paginate_posts(posts, request)
    
    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "page_title": "Posts from People You Follow"
    })


@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))
    
    # Check if the user is the owner of the post
    if post.user != request.user:
        return HttpResponseForbidden("You cannot edit this post.")
    
    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = PostEditForm(instance=post)
    
    return render(request, "network/edit_post.html", {
        "form": form,
        "post": post
    })


@login_required
def toggle_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)
    
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    
    if post.likes.filter(id=request.user.id).exists():
        # User has already liked this post, so unlike it
        post.likes.remove(request.user)
        liked = False
    else:
        # User hasn't liked this post yet, so like it
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })
