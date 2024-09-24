from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    """
    Model for handling friend requests between users.
    """
    sender = models.ForeignKey(
        User,
        related_name='friend_requests_sent',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='friend_requests_received',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('blocked', 'Blocked'),
        ),
        default='pending'
    )
    created_on = models.DateTimeField(null=True, auto_now_add=True)
    updated_on = models.DateTimeField(null=True, auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Friend request from {self.sender} to {self.receiver}"

    class Meta:
        unique_together = ('sender', 'receiver')  # Prevent duplicate friend requests


class Friendship(models.Model):
    """
    Model for storing active friendships between users.
    """
    user1 = models.ForeignKey(
        User,
        related_name='friendships',
        on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        User,
        related_name='friends_with',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(null=True, auto_now_add=True)
    updated_on = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        unique_together = ('user1', 'user2')  # Ensure unique friendship

    def __str__(self):
        return f"Friendship between {self.user1} and {self.user2}"


class UserLog(models.Model):
    class ActionChoice(models.TextChoices):
        SENTED = 'friend request sent'
        ACCEPTED = 'friend request accepted'
        DECLINED = 'friend request declined'
        BLOCKED = 'user blocked'
  
    action = models.CharField(max_length=72, choices=ActionChoice.choices)
    detail = models.CharField(max_length=512, null=True, blank=True)
    created_on = models.DateTimeField(null=True, auto_now_add=True)
    updated_on = models.DateTimeField(null=True, auto_now=True)
