from django.shortcuts import render
from django.views import View
from paypal.standard.forms import PayPalPaymentsForm


class PaymentView(View):

    def get(self, request):
        # What you want the button to do.
        paypal_dict = {
            "business": "sb-jc6dl844717@business.example.com",
            "amount": "30.6",
            "item_name": "aabbcctest",
            "invoice": "1324546089",
            "notify_url": "https://c15ae968.ngrok.io/api/online/paypal/",
            "return": "https://www.baidu.com",
            "cancel_return": "https://www.baidu.com",
            "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }

        # Create the instance.
        form = PayPalPaymentsForm(initial=paypal_dict)
        context = {"form": form}
        return render(request, "testPay.html", context)
