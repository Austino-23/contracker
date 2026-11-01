from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import MemberForm, ContributionForm, MemberRegistrationForm, AjoPayoutForm
from .models import Member, Contribution, AjoPayout, GroupSettings


def landing_page(request):
    """Public marketing homepage for ContriTrack."""
    return render(request, "savings/landing.html")


def admin_required(view):
    return login_required(user_passes_test(lambda u: u.is_staff or u.is_superuser)(view))

@login_required
def dashboard(request):
    is_admin = request.user.is_staff or request.user.is_superuser
    contributions = Contribution.objects.select_related("member")
    payouts = AjoPayout.objects.select_related("recipient")
    if not is_admin:
        try:
            member = request.user.member_profile
            contributions = contributions.filter(member=member)
            payouts = payouts.filter(recipient=member)
            member_count = 1
        except Member.DoesNotExist:
            contributions = contributions.none()
            payouts = payouts.none()
            member_count = 0
    else:
        member_count = Member.objects.filter(is_active=True).count()
    total = contributions.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    recent = contributions[:5]
    next_payout = payouts.filter(status=AjoPayout.STATUS_SCHEDULED).first()
    completed_payout_total = payouts.filter(status=AjoPayout.STATUS_COMPLETED).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return render(request, "savings/dashboard.html", {
        "member_count": member_count, "total_contributions": total,
        "recent_contributions": recent, "next_payout": next_payout,
        "completed_payout_total": completed_payout_total, "is_admin": is_admin,
        "group_settings": GroupSettings.current(),
        "completed_rounds": payouts.filter(status=AjoPayout.STATUS_COMPLETED).count(),
        "total_rounds": payouts.count(),
    })

@admin_required
def members_contributions(request):
    member_form = MemberForm()
    contribution_form = ContributionForm()
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_member":
            member_form = MemberForm(request.POST)
            if member_form.is_valid():
                member_form.save()
                messages.success(request, "Member added successfully.")
                return redirect("members_contributions")
        elif action == "record_contribution":
            contribution_form = ContributionForm(request.POST)
            if contribution_form.is_valid():
                contribution = contribution_form.save(commit=False)
                contribution.recorded_by = request.user
                contribution.save()
                messages.success(request, "Contribution saved successfully.")
                return redirect("members_contributions")
    contributions = Contribution.objects.select_related("member")
    this_month_total = contributions.filter(contribution_date__year=timezone.localdate().year, contribution_date__month=timezone.localdate().month).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return render(request, "savings/members_contributions.html", {"member_form": member_form, "contribution_form": contribution_form, "members": Member.objects.filter(is_active=True), "contributions": contributions[:100], "member_count": Member.objects.filter(is_active=True).count(), "this_month_total": this_month_total})

@login_required
def rotation_payouts(request):
    is_admin = request.user.is_staff or request.user.is_superuser
    payout_form = AjoPayoutForm()
    if request.method == "POST":
        if not is_admin:
            messages.error(request, "Only the administrator can manage payout rounds.")
            return redirect("rotation_payouts")
        action = request.POST.get("action")
        if action == "add_payout":
            payout_form = AjoPayoutForm(request.POST)
            if payout_form.is_valid():
                payout = payout_form.save(commit=False)
                payout.created_by = request.user
                payout.save()
                messages.success(request, f"Round {payout.round_number} was added to the payout schedule.")
                return redirect("rotation_payouts")
        elif action == "mark_paid":
            payout_id = request.POST.get("payout_id")
            payout = AjoPayout.objects.filter(pk=payout_id).first()
            if payout:
                payout.status = AjoPayout.STATUS_COMPLETED
                payout.payout_date = timezone.localdate()
                payout.save(update_fields=["status", "payout_date"])
                messages.success(request, f"Payout for {payout.recipient.full_name} marked as completed.")
            else:
                messages.error(request, "That payout round could not be found.")
            return redirect("rotation_payouts")
    payouts = AjoPayout.objects.select_related("recipient").all()
    if not is_admin:
        try:
            member = request.user.member_profile
            payouts = payouts.filter(recipient=member)
        except Member.DoesNotExist:
            payouts = payouts.none()
    completed_count = AjoPayout.objects.filter(status=AjoPayout.STATUS_COMPLETED).count() if is_admin else payouts.filter(status=AjoPayout.STATUS_COMPLETED).count()
    next_payout = payouts.filter(status=AjoPayout.STATUS_SCHEDULED).first()
    total_payouts = payouts.count()
    return render(request, "savings/rotation_payouts.html", {
        "payout_form": payout_form, "payouts": payouts, "is_admin": is_admin,
        "completed_count": completed_count, "total_payouts": total_payouts,
        "next_payout": next_payout,
    })

@login_required
def history_reports_settings(request):
    is_admin = request.user.is_staff or request.user.is_superuser
    if is_admin:
        contributions = Contribution.objects.select_related("member")
        payouts = AjoPayout.objects.select_related("recipient")
    else:
        try:
            member = request.user.member_profile
            contributions = Contribution.objects.select_related("member").filter(member=member)
            payouts = AjoPayout.objects.select_related("recipient").filter(recipient=member)
        except Member.DoesNotExist:
            contributions = Contribution.objects.none()
            payouts = AjoPayout.objects.none()

    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    if start_date:
        contributions = contributions.filter(contribution_date__gte=start_date)
        payouts = payouts.filter(scheduled_date__gte=start_date)
    if end_date:
        contributions = contributions.filter(contribution_date__lte=end_date)
        payouts = payouts.filter(scheduled_date__lte=end_date)

    total = contributions.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    payout_total = payouts.filter(status=AjoPayout.STATUS_COMPLETED).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    settings = GroupSettings.current()
    if request.method == "POST":
        if not is_admin:
            messages.error(request, "Only administrators can change group settings.")
            return redirect("history_reports_settings")
        settings.group_name = request.POST.get("group_name", settings.group_name).strip() or settings.group_name
        try:
            amount = Decimal(request.POST.get("contribution_amount", str(settings.contribution_amount)))
            if amount <= 0:
                raise ValueError
            settings.contribution_amount = amount
        except Exception:
            messages.error(request, "Contribution amount must be greater than zero.")
            return redirect("history_reports_settings")
        frequency = request.POST.get("contribution_frequency", settings.contribution_frequency)
        if frequency in dict(GroupSettings.FREQUENCY_CHOICES):
            settings.contribution_frequency = frequency
        start = request.POST.get("group_start_date") or None
        settings.start_date = start
        settings.save()
        messages.success(request, "Group settings saved successfully.")
        return redirect("history_reports_settings")

    return render(request, "savings/history_reports_settings.html", {
        "contributions": contributions[:200], "payouts": payouts[:200],
        "total": total, "payout_total": payout_total, "is_admin": is_admin,
        "group_settings": settings, "start_date": start_date, "end_date": end_date,
        "contribution_count": contributions.count(),
    })

@login_required
def export_report(request):
    is_admin = request.user.is_staff or request.user.is_superuser
    contributions = Contribution.objects.select_related("member")
    payouts = AjoPayout.objects.select_related("recipient")
    if not is_admin:
        try:
            member = request.user.member_profile
            contributions = contributions.filter(member=member)
            payouts = payouts.filter(recipient=member)
        except Member.DoesNotExist:
            contributions = contributions.none()
            payouts = payouts.none()
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="contritrack_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Date", "Member / Recipient", "Record Type", "Amount (NGN)", "Round", "Status"])
    for item in contributions.order_by("-contribution_date"):
        writer.writerow([item.contribution_date, item.member.full_name, "Contribution", item.amount, "", "Recorded"])
    for item in payouts.order_by("scheduled_date"):
        writer.writerow([item.payout_date or item.scheduled_date, item.recipient.full_name, "Payout", item.amount, item.round_number, item.get_status_display()])
    return response

def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "dashboard")
    return render(request, "savings/login.html", {"form": form})

def register_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = MemberRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your member account has been created.")
        return redirect("dashboard")
    return render(request, "savings/register.html", {"form": form})

def logout_page(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return redirect("dashboard")
