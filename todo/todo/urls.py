from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('task/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/list/done/', views.TaskListDoneView.as_view(), name='task_list_done'),
    path('task/<int:id>/', views.TaskDetailView.as_view(), name='task_detail'),
]
