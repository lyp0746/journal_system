# review/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 审稿人路由
    path('reviewer/dashboard/', views.reviewer_dashboard, name='reviewer_dashboard'),
    path('reviewer/invitation/<int:review_id>/', views.review_invitation_response, name='review_invitation_response'),
    path('reviewer/review/<int:review_id>/', views.review_paper, name='review_paper'),

    # 编辑路由
    path('editor/dashboard/', views.editor_dashboard, name='editor_dashboard'),
    path('editor/assign/<int:paper_id>/', views.assign_reviewers, name='assign_reviewers'),
    path('editor/decision/<int:paper_id>/', views.editor_decision, name='editor_decision'),
# review/urls.py (添加以下URL)
    path('statistics/', views.statistics_dashboard, name='statistics_dashboard'),
    path('statistics/export/submissions/', views.export_submissions_csv, name='export_submissions_csv'),
    path('statistics/export/reviews/', views.export_reviews_csv, name='export_reviews_csv'),
# review/urls.py
    path('statistics/review-duration/', views.review_duration_analysis, name='review_duration_analysis'),
]