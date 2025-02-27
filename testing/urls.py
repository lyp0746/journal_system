# testing/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.manage_test_accounts, name='manage_test_accounts'),
    path('accounts/create/', views.create_test_account, name='create_test_account'),
    path('accounts/<int:test_user_id>/', views.view_test_account, name='view_test_account'),
    path('accounts/<int:test_user_id>/delete/', views.delete_test_account, name='delete_test_account'),
    path('accounts/<int:test_user_id>/extend/', views.extend_test_account, name='extend_test_account'),
    # testing/urls.py (继续添加)
    path('dashboard/', views.test_dashboard, name='test_dashboard'),
    path('scenario/<int:scenario_id>/start/', views.start_test_scenario, name='start_test_scenario'),
    path('session/<int:session_id>/step/<int:step_number>/', views.test_step, name='test_step'),
    path('session/<int:session_id>/complete/', views.complete_test, name='complete_test'),
    # testing/urls.py (继续添加)
    path('session/<int:session_id>/feedback/', views.submit_test_feedback, name='submit_test_feedback'),
    path('feedbacks/', views.view_test_feedbacks, name='view_test_feedbacks'),
    # testing/urls.py (继续添加)
    path('analytics/', views.test_analytics_dashboard, name='test_analytics_dashboard'),
    path('analytics/data/', views.test_analytics_chart_data, name='test_analytics_chart_data'),
    path('report/', views.generate_test_report, name='generate_test_report'),
]