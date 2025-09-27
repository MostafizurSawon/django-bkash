from django.db import models

class PaymentLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    invoice_no = models.CharField(max_length=64, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=32, default='INITIATED')
    raw_request = models.TextField(blank=True, null=True)
    raw_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.invoice_no} ({self.status})"
