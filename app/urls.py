# APP-LEVEL URLS

from django.urls import path, include
from . import views
from .views import *

app_name = "app"

urlpatterns = [
    
    path("", include("django.contrib.auth.urls"), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/<str:username>/", views.ProfileView, name="profile"),
    path("accounts/edit_profile/", views.edit_profile, name="edit_profile"),
    path("accounts/password/", ChangePasswordView.as_view(template_name="registration/change_password.html"), name="change_password"),  
    
    
    path("home/", HomeView.as_view(), name="home"), # path extends a function
    path("post/<int:pk>/", PostView.as_view(), name="post_detail"),
    path("new_post/", NewPostView.as_view(), name="new_post"),
    path("post/<int:pk>/edit/", EditPostView.as_view(), name="edit_post"),
    path('post/<int:pk>/remove/', DeletePostView.as_view(), name='remove_post'),
    path('tags/<str:tag_slug>/', views.TagView, name='tag_posts'),
    path('saved/<int:post_id>/', views.saved_post, name='save_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path("post/<int:post_pk>/comment/<int:comment_pk>/remove/", views.delete_comment, name="remove_comment"),
    path("post/<int:post_pk>/comment/<int:comment_pk>/edit/", views.update_comment, name="edit_comment"),
    
    path("search/", views.search, name="search"),
    
    # path("chat/", views.chat, name="chat"),
    # path("directs/<username>", views.Directs, name="directs"),
    # path("send/", views.SendMessage, name="send-message"),
    # path("search/", views.UserSearch, name="search-users"),
    # path("new/<username>", views.NewConversation, name="conversation"),
    # path('notifications/', views.ShowNotifications, name='show-notifications'),
    # path('notifications/<noti_id>/delete', views.DeleteNotifications, name='delete-notifications'),

    
]
