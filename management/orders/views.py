from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from online.logger import online_logger
from online.order.models import Order

from utils.decorator import admin_auth


# 修改订单状态
class OderStatusChange(View):

    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    def put(self, request):
        if request.method == 'PUT':
            if request.body:
                try:
                    put = QueryDict(request.body)
                    order_no = put.get('order_no')
                    status = put.get('status')
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": 111, "errmsg": "请求数据不全或格式错误"})
                if status.isdigit() and order_no.isdigit():

                    try:
                        order = Order.objects.get(order_no=order_no)
                    except Order.DoesNotExist as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": 111, "errmsg": "订单不存在"})
                    except Exception as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": 111, "errmsg": "数据库错误"})

                    else:
                        if order.status == 2:
                            return JsonResponse({"errcode": 222, "errmsg": "订单已完成，不能修改状态"})
                        order = Order.objects.get(order_no=order_no)
                        order.status = status
                        order.save()
                        return JsonResponse({"errcode": 5, "errmsg": "订单状态修改成功"})
                else:
                    return JsonResponse({"errcode": 8, "errmsg": "订单状态或订单号不正确"})
            else:
                return JsonResponse({"errcode": 7, "errmsg": "未收到请求内容或请求方式错误"})
        else:
            return JsonResponse({"errcode": 6, "errmsg": "请求方式错误"})