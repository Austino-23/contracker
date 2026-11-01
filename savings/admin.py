from django.contrib import admin
from .models import GroupSettings, Member, Contribution, AjoPayout

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email", "is_active", "joined_at")
    search_fields = ("full_name", "phone", "email")
    list_filter = ("is_active",)

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "contribution_date", "recorded_by")
    list_filter = ("contribution_date",)
    search_fields = ("member__full_name",)


@admin.register(AjoPayout)
class AjoPayoutAdmin(admin.ModelAdmin):
    list_display = ("round_number", "recipient", "scheduled_date", "amount", "status", "payout_date")
    list_filter = ("status", "scheduled_date")
    search_fields = ("recipient__full_name",)
    ordering = ("round_number",)

admin.site.register(GroupSettings)
