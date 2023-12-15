from django.urls import path, include

from users.views import LoginView, VerifyTokenView, ProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('verify/<pk>', VerifyTokenView.as_view(), name="verify"),
    path('profile/', ProfileView.as_view(), name='profile')
]