from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("members-contributions/", views.members_contributions, name="members_contributions"),
    path("rotation-payouts/", views.rotation_payouts, name="rotation_payouts"),
    path("history-reports-settings/", views.history_reports_settings, name="history_reports_settings"),
    path("export-report/", views.export_report, name="export_report"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("logout/", views.logout_page, name="logout"),
]
