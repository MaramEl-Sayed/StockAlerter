from django.urls import path
from . import views

app_name = 'scheduler'

urlpatterns = [
    path('status/', views.SchedulerStatusView.as_view(), name='scheduler_status'),
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('start/', views.StartSchedulerView.as_view(), name='start_scheduler'),
    path('stop/', views.StopSchedulerView.as_view(), name='stop_scheduler'),
    path('restart/', views.RestartSchedulerView.as_view(), name='restart_scheduler'),
    path('jobs/<str:job_id>/pause/', views.PauseJobView.as_view(), name='pause_job'),
    path('jobs/<str:job_id>/resume/', views.ResumeJobView.as_view(), name='resume_job'),
    path('jobs/<str:job_id>/remove/', views.RemoveJobView.as_view(), name='remove_job'),
]
