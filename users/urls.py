from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import signup, login_view, activate_account

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(template_name='albums/album.html'), name='logout'),
    path('signup/', signup, name='signup'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
]
