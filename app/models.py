from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
from django.db.models.signals import post_save
from django.db.models import Max
from django.dispatch import receiver
import os
from PIL import Image

# Create your models here.

def user_directory_path_posts(instance, filename):
    # Upload files to user's media folder
    return f'user_{instance.poster.username}/posts/{filename}'

def user_directory_path_profile(instance, filename):
    # Upload files to user's media folder
    return f'user_{instance.user.username}/profile/{filename}'


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE)    
    img = models.ImageField(verbose_name='Image',blank=True, null=True, upload_to=user_directory_path_posts)
    caption = models.CharField(max_length=4094, blank=True, verbose_name="Caption")
    date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)
    likes = models.ManyToManyField(User, related_name="liked_posts")

    class Meta:
        verbose_name_plural = "Posts"
        
    # def __str__(self):
    #     return self.title + " | " + self.author.username
    
    # def get_absolute_url(self):
    #     return reverse("home", kwargs={"pk": self.pk})
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    pfp = models.ImageField(verbose_name='Profile Picture', blank=True, null=True, upload_to=user_directory_path_profile)
    location = models.CharField(max_length=64, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    saved = models.ManyToManyField(Post, blank=True, related_name='saved_by') # Favorites

    # For following and followers (related_name=followers automatically is opposite of following, all we need to do is reference related_name)
    following = models.ManyToManyField("self", related_name="followers", blank=True, symmetrical=False)  # if symmetrical is True it means that both must follow each other, as in the case of "add friend"

    def __str__(self):
        return str(self.user)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.pfp.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.pfp.path)
        
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: UserProfile.objects.get_or_create(user=instance))


class CommentPost(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)  
    commentor = models.ForeignKey(User, related_name="commentor", on_delete=models.CASCADE) 
    body = models.TextField(verbose_name="", blank=False, null=False)
    # body = RichTextField(verbose_name="", blank=True, null=True)
    comment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Comments"

    # def __str__(self):
    #     return f"{self.commentor.username} "
    

# class MessagePost(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
#     body = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)
#     is_read= models.BooleanField(default=False)
    
#     def sender_message(from_user, to_user, body):
#         # Sender
#         sender_message = MessagePost(
#             user = from_user,
#             sender = from_user,
#             receiver = to_user,
#             body = body,
#             is_read = True
#             )
#         sender_message.save()
        
#         # Receiver
#         receiver_message = MessagePost(
#             user = to_user,
#             sender = from_user,
#             receiver = from_user,
#             body = body,
#             is_read = True
#             )
#         receiver_message.save()
#         return sender_message
        
        
#     def get_message(user):
#         users = []
#         messages = MessagePost.objects.filter(user=user).values("receiver").annotate(last=Max('date')).order_by("-last")
#         for message in messages:
#             users.append({
#                 'user': User.objects.get(pk=message["receiver"]),
#                 'last': message["last"],
#                 'unread': MessagePost.objects.filter(user=user, receiver__pk=message["receiver"], is_read=False).count()
#             })
#         return users
                
                
# class Notifications(models.Model):
#     NOTIFICATION_TYPES = ((1, 'Like'), (2, 'Comment'), (3, 'Follow'))

#     post = models.ForeignKey("post.Post", on_delete=models.CASCADE, related_name="notification_post", null=True)
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_from_user" )
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_to_user" )
#     notification_types = models.IntegerField(choices=NOTIFICATION_TYPES, null=True, blank=True)
#     text_preview = models.CharField(max_length=100, blank=True)
#     date = models.DateTimeField(auto_now_add=True)
#     is_seen = models.BooleanField(default=False)
