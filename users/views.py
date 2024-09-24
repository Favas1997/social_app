from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from drf_spectacular.utils import extend_schema,OpenApiParameter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.core.cache import cache
from users import serializers, models, utils, throttles, constants
from django.db.models import Q



class SignIn(GenericViewSet):
    """
    API to SignIn from a user account.
    """
    serializer_class = serializers.SignInSerializer
    permission_classes = [AllowAny]
    throttle_classes = [throttles.SignInRateThrottle]

    @extend_schema(
        request=serializers.SignInSerializer,
        tags=['users'],
        responses={
            200: dict,
            400: dict
        }
    )
    def post(self, request):
        """
        POST request handler for user login.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email').lower()
        password = serializer.validated_data.get('password')

        user_obj = utils.get_user_by_email(email)

        if not user_obj:
            return Response(
                data={"detail": "No active account found with the given credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user_obj.check_password(password):
            return Response(
                data={"detail": "No active account found with the given credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user_obj.is_active:
            return Response(
                data={"detail": "You have not activated your account yet"},
                status=status.HTTP_404_NOT_FOUND
            )

        token_data = utils.get_tokens_for_user(user_obj)

        return Response(data=token_data)


class SignUp(APIView):
    """
    API to create account.
    """
    serializer_class    = serializers.SignUpSerializer
    permission_classes = [AllowAny]
    throttle_classes = [throttles.SignInRateThrottle]
    

    @extend_schema(
        request   = serializers.SignUpSerializer,
        tags=['users'],
        responses = {
            200: dict,
            400: dict
        }
    )
    def post(self,request):
        """
        POST request handler for user signup.
        """
        serializer = serializers.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email').lower()
        password = serializer.validated_data.get('password')
        name = serializer.validated_data.get('name', "")


        # Query user with the provided username
        user_obj = models.User.objects.filter(username=email).first()
 
        # Check if user with provided username exists
        if user_obj:
            return Response(data={"detail":"Email already exists"}, status=status.HTTP_404_NOT_FOUND)
        
        utils.create_user(email=email, password=password, name=name)
        return Response(data={"detail": "User added successfully"}, status=status.HTTP_200_OK)


class UserSearchAPIView(APIView):
    @extend_schema(
        tags=['users'],
        parameters=[
            OpenApiParameter(name='key', required=False, type=str,location=OpenApiParameter.QUERY),
            
        ],
        responses = None
    )
    def get(self, request):
        query = request.query_params.get('key', '').strip()

        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Determine if the query is an email or a name search
        if '@' in query:
            # Exact email match
            users = models.User.objects.filter(email__iexact=query)
        else:
            # Name search
            users = models.User.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).order_by("-created_on")

        # Return the paginated response
        data = utils.paginated_response(
            queryset=users, page_size=constants.DATA_PER_PAGE, serializer=serializers.UserModelSerializer, request=request)
        return data
    

class FriendRequestAPIView(APIView):
    """
        ViewSet for managing friend requests with error handling.
    """

    serializer_class    = serializers.FriendRequestSerializer
    

    @extend_schema(
        request   = serializers.FriendRequestSerializer,
        tags=['users'],
        responses = {
            200: dict,
            400: dict
        }
    )
    
    def post(self, request):
        """
        Send a friend request from the current user to another user.
        """
        serializer = serializers.FriendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receiver_id = serializer.validated_data.get('receiver_id')
        user = request.user
        # Cache key for friend request count
        cache_key = f'friend_requests_{request.user.id}'
        friend_request_count = cache.get(cache_key, 0)

        if friend_request_count >= constants.MAX_REQUEST_COUNT:
            return Response({'error': 'You can only send 3 friend requests per minute.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        try:
            receiver = models.User.objects.get(id=receiver_id)
            # Check if the sender or receiver is blocking each other
            if models.FriendRequest.objects.filter(sender=user, receiver=receiver,status=constants.RequestStatus.Blocked).exists():
                return Response({'error': 'You are blocked by this user and cannot send a friend request.'}, status=status.HTTP_403_FORBIDDEN)

            if models.FriendRequest.objects.filter(sender=receiver,receiver=user, status=constants.RequestStatus.Blocked).exists():
                return Response({'error': 'You have blocked this user and cannot send a friend request.'}, status=status.HTTP_403_FORBIDDEN)
            response = utils.send_friend_request(request.user, receiver, friend_request_count, cache_key)
            return Response(response, status=status.HTTP_201_CREATED)
        
        except models.User.DoesNotExist:
            return Response({"error": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        request   = serializers.FriendRequestAcknSerializer,
        tags=['users'],
        responses = {
            200: dict,
            400: dict
        }
    )
    def put(self, request):
        """
        Accept or reject a friend request.
        """

        serializer = serializers.FriendRequestAcknSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_id = serializer.validated_data.get('request_id')
        action = serializer.validated_data.get('action')
        try:
            friend_request = models.FriendRequest.objects.get(id=request_id)
            if action == constants.RequestStatus.Accepted:
                response = utils.accept_friend_request(friend_request)
            elif action == constants.RequestStatus.Rejected:
                response = utils.reject_friend_request(friend_request)
            else:
                return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(response, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        List all pending friend requests for the current user.
        """
        try:
            requests = models.FriendRequest.objects.select_related("sender").filter(receiver=request.user, status=constants.RequestStatus.Pending).order_by("-created_on")
            serializer = serializers.FriendRequestModelSerializer

            data = utils.paginated_response(
            queryset=requests, page_size=constants.DATA_PER_PAGE, serializer=serializer, request=request)
            return data
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FriendListAPIView(APIView):
    def get(self, request):
        user = request.user
        # Use a cache key to cache the user's friend list
        cache_key = f"friends_of_{user.id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Query for all users who accepted the friend request
        friends = models.Friendship.objects.select_related("user2").filter(
            user1=user
        ).order_by("-created_on")
        serializer = serializers.FriendRequestModelSerializer
        data = utils.paginated_response(
            queryset=friends, page_size=constants.DATA_PER_PAGE, serializer=serializer, request=request)

        # Store the result in the cache with a timeout
        cache.set(cache_key, data.data, timeout=constants.FRIEND_LIST_CACHE_TIMEOUT)  # Cache for 15 minutes
        return data