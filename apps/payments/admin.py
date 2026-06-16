from django.contrib import admin

# Register your models here.
from apps.payments.models import Refund

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):

    list_display = ("id", "order", "status", "amount")

    actions = ["approve_refund", "reject_refund"]

    def approve_refund(self, request, queryset):
        queryset.update(status="approved")

    def reject_refund(self, request, queryset):
        queryset.update(status="rejected")