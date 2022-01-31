from django.urls import path

from environment import views


urlpatterns = [
    path('', views.research_environments, name='research_environments'),
    path('identity-provisioning/', views.identity_provisioning, name='identity_provisioning'),
    path('billing-setup/', views.billing_setup, name='billing_setup'),
]