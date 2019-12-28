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


class OrdersView(View):
    """获取订单列表"""
    @method_decorator(csrf_exempt)
    @method_decorator(admin_auth)
    def get(self, request, user):

        username = request.GET.get("username", None)
        order_no = request.GET.get("order_no", "000")
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

        if username and phone:
            users = User.objects.filter(email__contains=email).filter(phone__contains=phone).filter(
                username__contains=username)
        elif username:
            users = User.objects.filter(email__contains=email).filter(username__contains=username)
        elif phone:
            users = User.objects.filter(email__contains=email).filter(username__contains=phone)
        elif email != '@':
            users = User.objects.filter(email__contains=email)
        else:
            users = User.objects.all()

        res = {"items": [], "total": 0}
        if users != '':
            orderss = []
            user_id = []
            for user in users:
                user_id.append(user.id)
            try:
                orders = Order.objects.filter(user_id__in=user_id).filter(
                    order_no__contains=order_no).filter(order_date__range=(start_date, end_date)).order_by('-id')
                total = len(orders)
                paginator = Paginator(orders, PER_PAGE_ORDER_COUNT)
                order_list = paginator.page(page)
                if total > 0:

                    for order in order_list:
                        user = User.objects.get(id=order.user_id)
                        user_name = user.username
                        user_email = user.email
                        user_phone = user.phone
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
                        res = {"items": orderss, "total": total}
                    return JsonResponse({"errcode": "0", "data": res})
                else:
                    return JsonResponse({"errcode": "0", "data": res})
            except Exception as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
        else:
            return JsonResponse({"errcode": "0", "data": res})


class OrderDetailView(View):
    """获取订单详情"""
    @method_decorator(csrf_exempt)
    @method_decorator(admin_auth)
    def get(self, request, user, order_no):
        try:
            if order_no is not None:
                request = request
                orders = Order.objects.filter(order_no=order_no)
                if orders != '':


                    order = orders[0]
                    user = User.objects.get(id=order.user_id)
                    user_name = user.username
                    user_email = user.email
                    user_phone = user.phone

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

    """修改订单状态"""
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    def put(self, request, order_no):
        type = request.GET.get('type', 'status')
        if type == "status":
            if request.body:
                try:
                    put = json.loads(request.body.decode())
                    status = put.get('status')
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": 111, "errmsg": "请求数据不全或格式错误"})
                if int(status):
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
                    # user_id = request.session.get('user_id')
                    user_id = 6
                    OrderStatusLog.objects.create(order_no=order_no, status=status, user_id=user_id,
                                                  change_date=time)
                    return JsonResponse({"errcode": 0, "errmsg": "订单状态修改成功"})
                else:
                    return JsonResponse({"errcode": 8, "errmsg": "订单状态不正确"})
            else:
                return JsonResponse({"errcode": 7, "errmsg": "未收到请求内容或请求方式错误"})
        else:
            return JsonResponse({"errcode": 6, "errmsg": "请求方式错误"})


class OrderLogsView(View):

    @method_decorator(csrf_exempt)
    def get(self, request, order_no):
        """获取订单日志"""
        try:
            if order_no is not None:
                states_log = []
                states = OrderStatusLog.objects.filter(order_no=order_no)
                lena = len(states)
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
