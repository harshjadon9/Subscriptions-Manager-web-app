from django.urls import path
from main import views

urlpatterns = [
    path('', views.index),
    path('add', views.add),
    path('delete', views.delete),
    path('add/submit', views.add_submit),
    path('login', views.login),
    path('signup', views.signup),
    path('postsignIn', views.postsignIn),
    path('postsignUp', views.postsignUp),
]
