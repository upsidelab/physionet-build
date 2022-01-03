from django.urls import path

from environment import views


urlpatterns = [
    path('', views.research_environments, name='research_environments')
]