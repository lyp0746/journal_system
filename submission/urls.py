# submission/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.paper_submission, name='paper_submission'),
    path('list/', views.submission_list, name='submission_list'),
    path('detail/<int:paper_id>/', views.submission_detail, name='submission_detail'),
    path('revise/<int:paper_id>/', views.paper_revision, name='paper_revision'),
    path('withdraw/<int:paper_id>/', views.withdraw_submission, name='withdraw_submission'),
]