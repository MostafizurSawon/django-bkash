from django.contrib import admin
from .models import PaymentLog

@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ('id','invoice_no','amount','status','created_at')
    list_filter = ('status','created_at')
    search_fields = ('invoice_no',)
