from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from .utils import get_token, create_payment, execute_payment, BKashError
from .models import PaymentLog
import uuid, json

@require_http_methods(["GET", "POST"])
def checkout(request: HttpRequest):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if not amount:
            messages.error(request, 'Amount is required.')
            return render(request, 'payments/checkout.html')
        invoice = f"INV-{uuid.uuid4().hex[:8].upper()}"
        log = PaymentLog.objects.create(invoice_no=invoice, amount=amount, status='INITIATED')
        try:
            id_token = get_token()
            data = create_payment(id_token, amount, invoice)
        except BKashError as e:
            log.status = 'TOKEN_OR_CREATE_FAILED'
            log.raw_response = str(e)
            log.save(update_fields=['status','raw_response'])
            messages.error(request, f'Error: {e}')
            return render(request, 'payments/checkout.html')

        # Save details in session
        request.session['bkash_id_token'] = id_token
        request.session['bkash_payment_id'] = data.get('paymentID')
        request.session['bkash_invoice'] = invoice

        # Persist request/response
        log.raw_response = json.dumps(data)
        log.status = 'REDIRECTED_TO_BKASH'
        log.save(update_fields=['status','raw_response'])

        bkash_url = data.get('bkashURL')
        if bkash_url:
            return redirect(bkash_url)
        messages.error(request, 'No redirect URL returned by bKash.')
        return render(request, 'payments/checkout.html')

    return render(request, 'payments/checkout.html')

@require_http_methods(["GET"])
def callback(request: HttpRequest):
    id_token = request.session.get('bkash_id_token')
    payment_id = request.session.get('bkash_payment_id')
    invoice = request.session.get('bkash_invoice')

    if not all([id_token, payment_id, invoice]):
        messages.error(request, 'Session expired or invalid. Please try again.')
        return render(request, 'payments/failed.html')

    log = PaymentLog.objects.filter(invoice_no=invoice).order_by('-id').first()
    try:
        result = execute_payment(id_token, payment_id)
    except BKashError as e:
        if log:
            log.status = 'EXECUTE_FAILED'
            log.raw_response = str(e)
            log.save(update_fields=['status','raw_response'])
        messages.error(request, f'Execute failed: {e}')
        return render(request, 'payments/failed.html')

    # Save final response
    if log:
        log.raw_response = json.dumps(result)
        log.save(update_fields=['raw_response'])

    status = result.get('transactionStatus') or result.get('statusCode')
    trx_id = result.get('trxID') or result.get('transactionID')
    if str(status).lower() == 'completed':
        if log:
            log.status = 'COMPLETED'
            log.save(update_fields=['status'])
        return render(request, 'payments/success.html', {'trx_id': trx_id, 'invoice': invoice})
    else:
        if log:
            log.status = f'FAILED:{status}'
            log.save(update_fields=['status'])
        return render(request, 'payments/failed.html', {'invoice': invoice, 'status': status})


from django.urls import reverse
from decimal import Decimal

PRODUCTS = [
    {'sku': 'P100', 'name': 'Pro Plan (1 mo)', 'price': Decimal('199.00')},
    {'sku': 'P200', 'name': 'Starter Pack', 'price': Decimal('99.00')},
    {'sku': 'P300', 'name': 'E-book', 'price': Decimal('49.00')},
]

def ping(request):
    return HttpResponse('pong')

def shop(request):
    context = {'products': PRODUCTS}
    return render(request, 'payments/shop.html', context)

@require_http_methods(["POST"])
def add_to_cart(request):
    sku = request.POST.get('sku')
    qty = int(request.POST.get('qty', '1'))
    prod = next((p for p in PRODUCTS if p['sku']==sku), None)
    if not prod:
        messages.error(request, 'Invalid product.')
        return redirect('payments:shop')
    cart = request.session.get('cart', {})
    cart[sku] = cart.get(sku, 0) + qty
    request.session['cart'] = cart
    messages.success(request, f"Added {qty} × {prod['name']}.")
    return redirect('payments:shop')

def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')
    for sku, qty in cart.items():
        prod = next((p for p in PRODUCTS if p['sku']==sku), None)
        if prod:
            line_total = prod['price'] * qty
            items.append({'sku': sku, 'name': prod['name'], 'price': prod['price'], 'qty': qty, 'line_total': line_total})
            total += line_total
    request.session['cart_total'] = str(total)
    return render(request, 'payments/cart.html', {'items': items, 'total': total})

def clear_cart(request):
    request.session['cart'] = {}
    messages.info(request, 'Cart cleared.')
    return redirect('payments:shop')

@require_http_methods(["GET"])
def tester(request):
    # quick check to see if token can be fetched with current creds
    try:
        id_token = get_token()
        ok = True
        msg = 'Token acquired'
    except Exception as e:
        ok = False
        msg = str(e)
    return render(request, 'payments/tester.html', {'ok': ok, 'message': msg})
