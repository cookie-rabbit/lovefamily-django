from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse, QueryDict
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from management.constants import PER_PAGE_ORDER_COUNT
from management.logger import management_logger
from management.user.models import User
from online.logger import online_logger
from online.order.models import Order, Order_Goods, OrderAddress, OrderStatusLog

from utils.decorator import admin_auth
from itertools import chain
import json


class OderStatusChange(View):

    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    def put(self, request):
        """修改订单状态"""
        if request.method == 'PUT':
            if request.body:
                try:
                    put = QueryDict(request.body)
                    order_no = put.get('order_no')
                    status = put.get('status')
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": 111, "errmsg": "请求数据不全或格式错误"})
                if status.isdigit():
                    try:
                        order = Order.objects.get(order_no=order_no)
                    except Order.DoesNotExist as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": 111, "errmsg": "订单不存在"})
                    except Exception as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": 111, "errmsg": "数据库错误"})

                    order.status = status
                    order.save()

                    time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
                    user_id = request.session.get("user_id", None)
                    OrderStatusLog.objects.create(order_no=order_no, status=status, user_id=user_id,
                                                  change_date=time)
                    return JsonResponse({"errcode": 0, "errmsg": "订单状态修改成功"})
                else:
                    return JsonResponse({"errcode": 8, "errmsg": "订单状态不正确"})
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
        order_no = request.GET.get("order_no", "0")
        email = request.GET.get("email", "@")
        phone = request.GET.get("phone", None)
        start_date = request.GET.get("start_date", "2000-01-01")
        end_date = request.GET.get("end_date", "2999-12-31")
        page = request.GET.get("page", 1)
        try:
            page = int(page)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "params errror"})
        # try:

        if username and phone:
            users = User.objects.filter(email__contains=email).filter(phone__contains=phone).filter(
                username__contains=username)
        elif username:
            users = User.objects.filter(email__contains=email).filter(username__contains=username)
        elif phone:
            users = User.objects.filter(email__contains=email).filter(username__contains=phone)
        else:
            users = User.objects.all()

        if users != '':
            orderss = []
            user_id = []
            for user in users:
                user_id.append(user.id)
            try:
                orders = Order.objects.filter(user_id__in=user_id, order_date__range=[start_date, end_date]).filter(
                    order_no__contains=order_no).order_by('-id')
                total = len(orders)
                paginator = Paginator(orders, PER_PAGE_ORDER_COUNT)
                order_list = paginator.page(page)
                if orders != '':
                    user_name = user.username
                    user_email = user.email
                    user_phone = user.phone
                    for order in order_list:
                        order_no = order.order_no
                        order_total = order.total
                        order_date = order.order_date
                        order_status = order.get_status_display()
                        order_details = Order_Goods.objects.filter(order_id=order.id)

                        order_count = 0
                        for order_detail in order_details:
                            good_count = order_detail.quantity
                            order_count += good_count
                        order_detail_res = {"order_no": order_no, "order_total": order_total,
                                            "order_date": order_date,
                                            "order_status": order_status, "order_quantity": order_count}
                        user_res = {"user_name": user_name, "user_email": user_email, "user_phone": user_phone}
                        com_res = {"user": user_res, "orders": order_detail_res}
                        orderss.append(com_res)
                    res = {"result": orderss, "total": total}
                    return JsonResponse({"errcode": "0", "data": res})
                else:
                    return JsonResponse({"errcode": "0", "data": '[]'})
            except Exception as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
        else:
            return JsonResponse({"errcode": "0", "data": ""})


class OrderDetailView(View):

    @method_decorator(csrf_exempt)
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取订单详情"""
        order_no = request.GET.get("order_no", None)
        try:
            if order_no is not None:
                orders = Order.objects.filter(order_no=order_no)
                if orders != '':

                    user_name = user.username
                    user_email = user.email
                    user_phone = user.phone
                    order = orders[0]
                    order_no = order.order_no
                    order_total = order.total
                    order_date = order.order_date
                    order_status = order.status
                    order_details = Order_Goods.objects.filter(order_id=order.id)
                    goods = []

                    order_count = 0
                    for order_detail in order_details:
                        good_name = order_detail.name_en
                        good_description = order_detail.description_en
                        good_count = order_detail.quantity
                        order_count += good_count
                        good_price = order_detail.on_price
                        good_img = str(order_detail.img)
                        '''还需要地址，并将数据进行拼接'''
                        good_res = {"good_name": good_name, "good_description": good_description,
                                    "good_count": good_count, "good_price": good_price,
                                    "good_img": good_img}
                        goods.append(good_res)
                    order_add = OrderAddress.objects.get(id=order.address_id)
                    name = order_add.name
                    city = order_add.city
                    district = order_add.district
                    road = order_add.road
                    postcode = order_add.postcode
                    phone_num = order_add.phone_number
                    province = order_add.province
                    order_detail_res = {"order_no": order_no, "order_total": order_total,
                                        "order_date": order_date,
                                        "order_status": order_status, "order_quantity": order_count}
                    add_res = {"name": name, "city": city, "district": district, "road": road,
                               "postcode": postcode, "phone_num": phone_num, "province": province}
                    order_res = {"goods": goods, "order": order_detail_res, "address": add_res}
                    user_res = {"user_name": user_name, "user_email": user_email, "user_phone": user_phone}
                    com_res = {"user": user_res, "orders": order_res}
                    res = com_res
                    return JsonResponse({"errcode": "0", "data": res})
                else:
                    return JsonResponse({"errcode": "0", "data": '[]'})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})


class OrderStatusView(View):

    @method_decorator(csrf_exempt)
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取订单状态变更详情"""
        order_no = request.GET.get("order_no", None)
        try:
            if order_no is not None:
                states_log = []
                states = OrderStatusLog.objects.filter(order_no=order_no)
                sta_dic = {1: "orderd", 2: "Payed", 3: "Delivering", 4: "Finished", 5: "Closed"}

                if states != '':
                    for state in states:
                        status = sta_dic.get(state.status)
                        try:
                            username = User.objects.get(id=state.user_id).username
                        except Exception as e:
                            management_logger.error(e)
                            return JsonResponse({"errcode": "102", "errmsg": "db error"})
                        date = state.change_date
                        state_log = {"status": status, "user": username, "date": date}
                        states_log.append(state_log)
                res = states_log
                return JsonResponse({"errcode": "0", "data": res})
            else:
                return JsonResponse({"errcode": "0", "data": '[]'})

        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
