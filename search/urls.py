from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.search, name='search'),
    path('history/', views.history, name='history'),
    path('history/delete/<int:query_id>/', views.delete_history, name='delete_history'),
    path('history/clear/', views.clear_history, name='clear_history'),
]
