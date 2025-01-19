from django.urls import path, include
from strivers import views

app_name = 'strivers'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('authorize/', views.authorize, name='authorize'),
    path('callback/', views.authorization_callback, name='callback'),
    path('store_cookie/', views.store_cookie, name='store_cookie'),
    path('get_activities/', views.get_activities, name='get_activities'),
    path('analysis_tools/', views.analysis_tools, name='analysis_tools'),
    path('logout/', views.logout, name='logout'),
]
