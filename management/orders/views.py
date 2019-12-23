from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from management.logger import management_logger
from management.user.models import User
from online.logger import online_logger
from online.order.models import Order,Order_Goods

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


class OrdersView(View):

    @method_decorator(csrf_exempt)
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取订单列表"""
        username = request.GET.get("username", None)
        order_no = request.GET.get("order_no", None)
        email = request.GET.get("email", None)
        phone = request.GET.get("phone", None)
        start_date = request.GET.get("start_date", '2000-01-01')
        end_date = request.GET.get("end_date", '2999-12-12')
        page = request.GET.get("page", 1)
        try:
            page = int(page)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "params errror"})

        try:
            aa = []
            bb = []
            cc = []
            order_count = 0
            if order_no:
                pass
            else:
                if username and phone and email:

                    users = User.objects.filter(email__contains=email).filter(phone__contains=phone).filter(
                        username__contains=username)
                    for user in users:
                        user_name = user.username
                        user_email = user.email
                        user_phone = user.phone
                        orders = Order.objects.filter(user_id=user.id, date__range=(start_date, end_date))
                        if orders != '':
                            for order in orders:
                                order_no = order.order_no
                                order_total = order.total
                                order_date = order.order_date
                                order_status = order.status
                                order_details = Order_Goods.objects.filter(order_id=order.id)
                                for order_detail in order_details:
                                    good_name = order_detail.name_en
                                    good_description = order_detail.description_en
                                    good_count = order_detail.quantity
                                    order_count += good_count
                                    good_price = order_detail.on_price
                                    good_img = order_detail.img
                                    '''还需要地址，并将数据进行拼接'''

                        else:
                            pass

                elif username and phone:
                    users = User.objects.filter(username__contains=username).filter(phone__contains=phone)
                elif username and email:
                    users = User.objects.filter(username__contains=username).filter(email__contains=email)
                elif phone and email:
                    users = User.objects.filter(phone__contains=phone).filter(email__contains=email)
                else:
                    users = User.objects.all()
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
