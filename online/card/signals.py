from django.shortcuts import get_object_or_404
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from mobile.logger import payment_logger
from online.order.models import Order


def payment_success(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # payment was successful
        order = get_object_or_404(Order, order_no=ipn_obj.invoice)
        # mark the order as paid
        order.status = 2
        order.paid_date = ipn_obj.payment_date
        order.save()
        # record the payment in orders log
        created_at = ipn_obj.created_at  # 创建日期
        invoice = ipn_obj.invoice  # 订单号
        name = ipn_obj.address_name  # 支付人姓名
        payment_date = ipn_obj.payment_date  # 支付日期
        payment_status = ipn_obj.payment_status  # 支付状态
        txn_id = ipn_obj.txn_id  # 平台订单号
        text = "This INFO comes from payment_success, {} has make a order_no {} at {}, and payed at {}, " \
               "the txn_id is {}, the payment_status is {}".format(name, invoice, created_at, payment_date, txn_id,
                                                                   payment_status)
        payment_logger.info(text)


def payment_failure(sender, **kwargs):
    ipn_obj = sender
    created_at = ipn_obj.created_at  # 创建日期
    invoice = ipn_obj.invoice  # 订单号
    name = ipn_obj.address_name  # 支付人姓名
    payment_date = ipn_obj.payment_date  # 支付日期
    payment_status = ipn_obj.payment_status  # 支付状态
    txn_id = ipn_obj.txn_id  # 平台订单号
    text = "This INFO comes from payment_failure, {} has make a order_no {} at {}, and payed at {}, " \
           "the txn_id is {}, the payment_status is {}".format(name, invoice, created_at, payment_date, txn_id,
                                                               payment_status)
    payment_logger.info(text)


valid_ipn_received.connect(payment_success)
invalid_ipn_received.connect(payment_failure)
