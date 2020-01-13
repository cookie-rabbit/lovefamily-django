from django.shortcuts import render
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm

from weigan_shopping import settings


class PaymentView(View):
    def __init__(self, request, order_no, total, **kwargs):
        super().__init__(**kwargs)
        self.request = request
        self.order_no = order_no
        self.total = total

    def pay(self):
        # What you want the button to do.
        paypal_dict = {
            "business": settings.PAYMENT_BUSSINESS,
            "amount": self.total,
            "item_name": settings.PAYMENT_ITEM,
            "invoice": self.order_no,
            "notify_url": settings.PAYMENT_NOTIFY_URL,
            "return": settings.PAYMENT_RETURN_URL,
            "cancel_return": settings.PAYMENT_CANCEL_URL + self.order_no,
            "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }

        # Create the instance.
        form = PayPalPaymentsForm(initial=paypal_dict)
        context = {"form": form}
        return render(self.request, "testPay.html", context)
