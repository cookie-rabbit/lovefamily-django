# from django.shortcuts import get_object_or_404
# from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
# from paypal.standard.models import ST_PP_COMPLETED
#
# from online.order.models import Order
#
#
# def payment_success(sender, **kwargs):
#     ipn_obj = sender
#     if ipn_obj.payment_status == ST_PP_COMPLETED:
#         # payment was successful
#         order = get_object_or_404(Order, order_no=ipn_obj.invoice)
#         # mark the order as paid
#         order.status = 2
#         order.save()
#         print("success")
#     print("pending")
#
#
# def payment_failure(sender, **kwargs):
#     ipn_obj = sender
#     print("failed")
#
#
# valid_ipn_received.connect(payment_success)
# invalid_ipn_received.connect(payment_failure)
