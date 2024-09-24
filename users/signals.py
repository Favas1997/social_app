from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from users import models, constants


# Userlog for acknowledge request
@receiver(pre_save, sender=models.FriendRequest)
def request_acknowledge(sender, instance, **kwargs):
    if instance.status == constants.RequestStatus.Accepted :
        models.UserLog.objects.create(
            action=models.UserLog.ActionChoice.ACCEPTED,
            detail=f"""friend request accepted by {instance.receiver.first_name}"""
        )
    elif instance.status == constants.RequestStatus.Rejected :
        models.UserLog.objects.create(
            action=models.UserLog.ActionChoice.DECLINED,
            detail=f"""friend request declined by {instance.receiver.first_name}"""
        )
    elif instance.status == constants.RequestStatus.Blocked :
        models.UserLog.objects.create(
            action=models.UserLog.ActionChoice.BLOCKED,
            detail=f"""Action blocked by {instance.receiver.first_name}"""
        )


# Userlog for request create
@receiver(post_save, sender=models.FriendRequest)
def request_created(sender, instance, created, **kwargs):
    if created:
        models.UserLog.objects.create(
            action=models.UserLog.ActionChoice.SENTED,
            detail=f"""Friend request sented to {instance.receiver.first_name}"""
        )


    