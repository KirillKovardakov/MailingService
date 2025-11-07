from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView, toggle_block_user, users_list, deactivate_mailing

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html', next_page='mailing:dashboard'), name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('manage/users/', users_list, name='users_list'),
    path('manage/users/<int:user_id>/block/', toggle_block_user, name='toggle_block_user'),
    path('manage/mailings/<int:mailing_id>/disable/', deactivate_mailing, name='disable_mailing'),

]
