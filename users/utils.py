from users import models, constants
from generics import pagination
from django.utils import timezone
from datetime import timedelta, datetime

from rest_framework_simplejwt.tokens import RefreshToken

from django.db import IntegrityError
from django.core.cache import cache
from django.core.exceptions import ValidationError


def create_user(name: str, email: str, password: str) -> models.User:
    """
    Creates a new user with the given name, email, and password.

    Args:
        name (str): The user's first name.
        email (str): The user's email address.
        password (str): The user's password.

    Returns:
        User: The created user object.

    Raises:
        ValueError: If the email is already in use or if any other validation fails.
        IntegrityError: If there is a database error such as a unique constraint violation.
    """
    try:
        user = models.User.objects.create_user(
            username=email,  # Username should be unique
            email=email,
            password=password,
            first_name = name
        )
        return user
    except IntegrityError:
        raise ValueError("A user with this email already exists.")
    except ValidationError as e:
        raise ValueError(f"Validation error: {e}")
    except Exception as e:
        # Handle any other exceptions
        raise RuntimeError(f"An unexpected error occurred: {e}")


def get_user_by_email(email: str):
        """
        Retrieve a user by email address.
        """
        return models.User.objects.filter(email=email).first()


def get_tokens_for_user(user_obj: models.User):
    """
    Generate authentication tokens for the user.
    """
    refresh = RefreshToken.for_user(user_obj)
    return {
        'user_id': user_obj.id,
        'email': user_obj.email,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def send_friend_request(sender, receiver, friend_request_count,cache_key):
    """
    Sends a friend request from sender to receiver.
    """
    try:
        if sender == receiver:
            raise ValidationError("You cannot send a friend request to yourself.")
        
        friend_request, created = models.FriendRequest.objects.get_or_create(
            sender=sender, receiver=receiver,
        )

        # Check if a previous request was rejected and if the cooldown period has passed
        try:
            if friend_request.status == constants.RequestStatus.Rejected:
                cooldown_period = timedelta(hours=constants.FRIEND_REQUEST_COOLDOWN_HOURS)
                # If the last rejection was within the cooldown period, block the request
                if friend_request.updated_on and timezone.now() - friend_request.updated_on < cooldown_period:
                    return {
                        'error': f'You cannot send another request until the cooldown period has passed. Please wait {constants.FRIEND_REQUEST_COOLDOWN_HOURS} hours.'
                    }
                else:
                    friend_request.status = constants.RequestStatus.Pending
                    friend_request.updated_on = datetime.now()
                    friend_request.save()
                    return {"message": "Friend request sent."}
            else:
                pass
        except models.FriendRequest.DoesNotExist:
            pass
        if not created:
            if friend_request.status == constants.RequestStatus.Pending:
                return {"message": "Friend request already sent."}
            elif friend_request.status == constants.RequestStatus.Accepted:
                return {"message": "You are already friends."}
        
        # Increment the friend request count and set cache timeout to 60 seconds
        cache.set(cache_key, friend_request_count + constants.FRIEND_REQUEST_INC, timeout=constants.FRIEND_REQUEST_CACHE_TIMEOUT)
        return {"message": "Friend request sent."}
    
    except ValidationError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


def reject_friend_request(request):
    """
    Rejects a pending friend request.
    """
    try:
        if request.status != 'pending':
            return {"error": "This friend request has already been handled."}

        request.status = 'rejected'
        request.updated_on = datetime.now()
        request.save()
        return {"message": "Friend request rejected."}
    
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


def accept_friend_request(request):
    """
    Accepts a pending friend request and creates a Friendship.
    """
    try:
        if request.status != 'pending':
            return {"error": "This friend request has already been handled."}
        request.status = 'accepted'
        request.updated_on = datetime.now()
        request.save()
        # Create the friendship
        models.Friendship.objects.create(user1=request.sender, user2=request.receiver)
        clear_user_friend_cache(request.sender.id)
        clear_user_friend_cache(request.receiver.id)
        return {"message": "Friend request accepted."}
    
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}




def paginated_response(page_size='page_size',queryset='queryset',request='request',serializer='serializer'):
    """
    page_size is for number of items to show in a page
    queryset is for data retrive from the table
    serializer is for the data to be serialized
    this function returns the data to be shown in the page
    """
    paginator = pagination.CustomPagination(page_size=page_size)
    page = paginator.paginate_queryset(queryset,request)
    serializer = serializer(page,many=True)
    return paginator.get_paginated_response(serializer.data)


def clear_user_friend_cache(user_id):
    """
    Clears the cached friend list of a specific user.
    
    Args:
        user_id (int): The ID of the user whose friend list cache needs to be cleared.
    
    Returns:
        None
    """
    cache_key = f"friends_of_{user_id}"
    cache.delete(cache_key)

