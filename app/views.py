from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from django.views.generic.edit import FormMixin
from django.urls import reverse, reverse_lazy 
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from app.models import *
from .forms import UserRegisterForm, PostForm, EditProfileForm, ChangePasswordForm, ProfileForm, CommentForm
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from taggit.models import Tag
from django.core.paginator import Paginator

# Create your views here.

# HOMEPAGE

# def home(request):
#     posts = BlogPost.objects.all()
#     return render(request, "blog/home.html", context=posts)

class HomeView(LoginRequiredMixin, ListView):
    login_url = "/login/"
    redirect_field_name = 'redirect_to'
    template_name = "home.html"
    model = Post
    # queryset = BlogPost.objects.all()
    context_object_name = "posts"
    ordering = ["-date"]  # "-id" also works since latest post id is equal to previous post id + 1
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Post.objects.all().order_by("-date")
        else:
            following = self.request.user.userprofile.following.all()
            following_users = User.objects.filter(userprofile__in=following)
            # return BlogPost.objects.filter(author__in=following_users)
            return Post.objects.filter(Q(poster__in=following_users) | Q(poster=self.request.user)).order_by("-date")
    
class PostView(FormMixin, DetailView):
    template_name = "post_detail.html"
    model = Post
    context_object_name = "post"
    form_class = CommentForm
    
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.id})
    
    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        context['form'] = CommentForm(initial={'post': self.object})
        context["comment_post"] = True
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        form.instance.post = self.object
        form.instance.commentor = self.request.user
        comment = form.save(commit=False)
        comment.save()
        return HttpResponseRedirect(f"{reverse('app:post_detail', kwargs={'pk': self.object.id})}?scroll_to_comment=true")
    
# CREATE POST
class NewPostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "new_post.html"
    
    def get_success_url(self):
        # return reverse_lazy('app:post_detail', kwargs={'pk': self.object.pk})
        return reverse_lazy('app:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request_path'] = self.request.path
        return context
        
    
    def form_valid(self, form):
        form.instance.poster = self.request.user
        return super().form_valid(form)
    

# EDIT POST
class EditPostView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "edit_post.html"
    
    def get_success_url(self):
        return reverse_lazy('app:post_detail', kwargs={'pk': self.object.pk})


# DELETE POST 
class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "remove_post.html"
    context_object_name = "post"

    def get_success_url(self):
        return reverse('app:profile', kwargs={'username': self.object.poster.username})
    

# TAGS
def TagView(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags__in=[tag]).order_by('-date')
    return render(request, 'tag_posts.html', {'tag': tag, 'posts': posts})

# UPDATE COMMENT
def update_comment(request, post_pk, comment_pk):
    comment = get_object_or_404(CommentPost, pk=comment_pk)
    if comment.commentor != request.user and request.user.id != 1:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('app:post_detail', pk=post_pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_post.html', {"form":form, "comment":comment})

    
# DELETE COMMENT
def delete_comment(request, post_pk, comment_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment = get_object_or_404(CommentPost, pk=comment_pk, post=post)
    if comment.commentor != request.user and request.user.id != 1:
        # Return an error message if the comment was not made by the current user
        return HttpResponseForbidden()
    if request.method == 'POST':
        comment.delete()
        return redirect('app:post_detail', pk=post.pk)
    return render(request, 'remove_post.html', {'comment': comment, "post":post})
    

# PROFILE
def ProfileView(request, username):
    user_posts = Post.objects.filter(poster__username=username).order_by("-date")
    saved_posts = request.user.userprofile.saved.all().order_by("-date")
    num_posts = user_posts.count()
    host = User.objects.get(username=username)
    host_profile = UserProfile.objects.get(user=host)
    current_user = None
    if request.user.is_authenticated:
        current_user = request.user.userprofile
    num_followers = host.userprofile.followers.count()
    num_following = host.userprofile.following.count()

    # Fetching followers and following list
    followers = host_profile.followers.all()
    following = host_profile.following.all()

    # Fetching posts, followers and following count for each follower
    for follower in followers:
        follower.num_posts = Post.objects.filter(poster=follower.user).count()
        follower.num_followers = follower.user.userprofile.followers.count()
        follower.num_following = follower.user.userprofile.following.count()

    # Fetching posts, followers and following count for each following
    for follows in following:
        follows.num_posts = Post.objects.filter(poster=follows.user).count()
        follows.num_followers = follows.user.userprofile.followers.count()
        follows.num_following = follows.user.userprofile.following.count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action', '')
        if action == 'follow' or action == 'unfollow':
            try:
                user_profile = UserProfile.objects.get(user__username=username)
                if action == "unfollow":
                    current_user.following.remove(user_profile)
                    return JsonResponse({'status':'ok', 'action':'unfollow'})
                elif action == "follow":
                    current_user.following.add(user_profile)
                    return JsonResponse({'status':'ok', 'action':'follow'})
            except Exception as e:
                return JsonResponse({'status':'error', 'error': str(e)})

    context = {
        "username": username, 
        "user_posts": user_posts, 
        "saved_posts": saved_posts, 
        "host": host, 
        'num_posts': num_posts, 
        'num_followers': num_followers, 
        'num_following': num_following,
        "followers": followers,
        "following": following,
        "current_user": current_user
    }

    return render(request, "profile.html", context)


# LIKE
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        # User already liked the post, so unlike it
        post.likes.remove(user)
        liked = False
    else:
        # User hasn't liked the post, so like it
        post.likes.add(user)
        liked = True

    # Return the updated like count and liked status
    like_count = post.likes.count()
    return JsonResponse({"liked": liked, "count": like_count})

# FAVORITES
def saved_post(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    if post in user.userprofile.saved.all():
        # Post is already saved, so un-save it
        user.userprofile.saved.remove(post)
        saved = False
    else:
        # Post is not saved, so save it
        user.userprofile.saved.add(post)
        saved = True
    return JsonResponse({"saved": saved})

# REGISTER
class SignUpView(SuccessMessageMixin, CreateView):
    form_class = UserRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("app:login")
    success_message = 'Account created successfully! Please login.'
    
    
# Edit Profile with UserProfile fields
@login_required
@transaction.atomic
def edit_profile(request):
    if request.method == "POST":
        user_form = EditProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.userprofile)   
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            current_user = request.user.username
            return redirect('app:profile', current_user)
    else:
        user_form = EditProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.userprofile)
    return render(request, "registration/edit_profile.html", {"user_form":user_form, "profile_form": profile_form})


# CHANGE PASSWORD 
class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    # form_class = PasswordChangeForm
    form_class = ChangePasswordForm
    success_url = reverse_lazy("app:login")
    success_message = 'Password changed successfully! Please login.'

    def form_valid(self, form):
        form.save()
        self.request.session.flush()
        logout(self.request)
        return super().form_valid(form)
    

from django.db.models import Q
def search(request):
    query = request.GET.get("query", "")
    posts = Post.objects.filter(Q(tags__name__icontains=query) | Q(poster__username__icontains=query)).order_by('-date').distinct()
    return render(request, "search.html", {"posts":posts, "query":query})
    
    
# @login_required
# def chat(request):
#     user = request.user
#     messages = MessagePost.get_message(user=user)
#     active_direct = None
#     directs = None
    
#     if messages:
#         message = messages[0]
#         active_direct = message["user"].username
#         directs = MessagePost.objects.filter(user=user, receiver=message["user"])
#         directs.update(is_read=True)
        
#         for message in messages:
#             if message["user"].username == active_direct:
#                 message["unread"] = 0
#     context = {
#         "directs": directs,
#         "active_direct": active_direct,
#         "messages": messages,
#     }
                
#     return render(request, "chat.html", context)


# @login_required
# def Directs(request, username):
#     user  = request.user
#     messages = MessagePost.get_message(user=user)
#     active_direct = username
#     directs = MessagePost.objects.filter(user=user, receiver__username=username)  
#     directs.update(is_read=True)

#     for message in messages:
#             if message['user'].username == username:
#                 message['unread'] = 0
#     context = {
#         'directs': directs,
#         'messages': messages,
#         'active_direct': active_direct,
#     }
#     return render(request, 'directs.html', context)


# def SendMessage(request):
#     from_user = request.user
#     to_user_username = request.POST.get('to_user')
#     body = request.POST.get('body')

#     if request.method == "POST":
#         to_user = User.objects.get(username=to_user_username)
#         MessagePost.sender_message(from_user, to_user, body)
#         return redirect('app:chat')

# def UserSearch(request):
#     query = request.GET.get('q')
#     context = {}
#     if query:
#         users = User.objects.filter(Q(username__icontains=query))

#         # Paginator
#         paginator = Paginator(users, 8)
#         page_number = request.GET.get('page')
#         users_paginator = paginator.get_page(page_number)

#         context = {
#             'users': users_paginator,
#             }

#     return render(request, 'search.html', context)

# def NewConversation(request, username):
#     from_user = request.user
#     body = ''
#     try:
#         to_user = User.objects.get(username=username)
#     except Exception as e:
#         return redirect('search')
#     if from_user != to_user:
#         MessagePost.sender_message(from_user, to_user, body)
#     return redirect('app:chat')


# # Notifications
# def ShowNotifications(request):
#     user = request.user
#     notifications = Notifications.objects.filter(user=user).order_by('-date')

#     context = {
#         'notifications': notifications,

#     }
#     return render(request, 'notifications.html', context)

# def DeleteNotifications(request, noti_id):
#     user = request.user
#     Notifications.objects.filter(id=noti_id, user=user).delete()
#     return redirect('app:show-notifications')
