
from rest_framework_simplejwt import views as jwt_views
from django.urls import path, include
from users import views


urlpatterns = [
    path('sign-in', views.SignIn.as_view({"post": "post"}), name='sign_in'),
    path('sign-up', views.SignUp.as_view(), name='sign_up'),
    path('refresh', jwt_views.TokenRefreshView.as_view(), name='refresh'),
    path('users/search/', views.UserSearchAPIView.as_view(), name='user-search'),
    path('friend-request/', views.FriendRequestAPIView.as_view(), name='send-friend-request'),
    path('friends/', views.FriendListAPIView.as_view(), name='friend-list'),
    
]
