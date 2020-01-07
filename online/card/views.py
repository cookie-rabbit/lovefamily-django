from django.core.urlresolvers import reverse
from django.dispatch import Signal
from django.shortcuts import render
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm
import signal


class PaymentView(View):

    def get(self, request):
        # What you want the button to do.
        paypal_dict = {
            "business": "862151891@qq.com",
            "amount": "10",
            "item_name": "name of the item",
            "invoice": "unique-invoice-id",
            "notify_url": "https://www.baidu.com",
            "return": "https://www.baidu.com",
            "cancel_return": "https://www.baidu.com",
            "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }

        # Create the instance.
        form = PayPalPaymentsForm(initial=paypal_dict)
        context = {"form": form}
        return render(request, "testPay.html", context)


class CheckView(View):

    def post(self, request):
        abc = request
        print('abc')
