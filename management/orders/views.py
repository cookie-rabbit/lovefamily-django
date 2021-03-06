from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse, QueryDict
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from management.constants import PER_PAGE_ORDER_COUNT
from management.logger import management_logger
from management.user.models import User, Admin
from online.logger import online_logger
from online.order.models import Order, Order_Goods, OrderAddress, OrderStatusLog

from utils.decorator import admin_auth
import json

from weigan_shopping import settings


class OrdersView(View):
    """获取订单列表"""

    @method_decorator(csrf_exempt)
    @method_decorator(admin_auth)
    def get(self, request, user):

        username = request.GET.get("username", None)
        order_no = request.GET.get("order_no", "000")
        email = request.GET.get("email", "@")
        status = request.GET.get("status", 0)
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
                username__icontains=username)
        elif username:
            users = User.objects.filter(email__contains=email).filter(username__icontains=username)
        elif phone:
            users = User.objects.filter(email__contains=email).filter(phone__contains=phone)
        elif email != '@':
            users = User.objects.filter(email__contains=email)
        else:
            users = User.objects.all()

        res = {"items": [], "total": 0}
        if users != '':
            orderss = []
            user_id = []
            try:
                status = int(status)
            except Exception as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "101", "errmsg": "Params error"})
            for user in users:
                user_id.append(user.id)
            try:
                if status in [1, 2, 3, 4, 5]:
                    orders = Order.objects.filter(user_id__in=user_id).filter(order_no__contains=order_no).filter(
                        order_date__range=(start_date, end_date)).filter(status=status).order_by('-id')
                elif status == 0:
                    orders = Order.objects.filter(user_id__in=user_id).filter(order_no__contains=order_no).filter(
                        order_date__range=(start_date, end_date)).order_by('-id')
                else:
                    return JsonResponse({"errcode": "101", "errmsg": "Params error"})
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
                        order_date = order.order_date.strftime("%Y-%m-%d %H:%M:%S")
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
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        else:
            return JsonResponse({"errcode": "0", "data": res})


class OrderDetailView(View):
    """获取订单详情"""

    @method_decorator(csrf_exempt)
    @method_decorator(admin_auth)
    def get(self, request, user, order_no):
        try:
            if order_no is not None:
                orders = Order.objects.filter(order_no=order_no)
                if orders != '':

                    order = orders[0]
                    user = User.objects.get(id=order.user_id)
                    user_name = user.username
                    user_email = user.email
                    user_phone = user.phone

                    order_no = order.order_no
                    order_total = order.total
                    order_date = order.order_date.strftime("%Y-%m-%d %H:%M:%S")
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
                                    "good_img": settings.URL_PREFIX + '/media/' + good_img}
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
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})

    """修改订单状态"""

    @method_decorator(admin_auth)
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    def put(self, request, user, order_no):
        type = request.GET.get('type', 'status')
        if type == "status":
            if request.body:
                try:
                    put = json.loads(request.body.decode())
                    status = put.get('status')
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": "101", "errmsg": "params errror"})
                if int(status):
                    try:
                        order = Order.objects.get(order_no=order_no)
                    except Order.DoesNotExist as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": "111", "errmsg": "order not exist"})
                    except Exception as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": "102", "errmsg": "Db error"})
                    order.status = status
                    order.save()

                    time = timezone.localtime(timezone.now())
                    user_id = request.session.get('admin_id')
                    OrderStatusLog.objects.create(order_no=order_no, status=status, user_id=user_id,
                                                  change_date=time, is_admin=True)
                    return JsonResponse({"errcode": 0, "errmsg": "update success"})
                else:
                    return JsonResponse({"errcode": "101", "errmsg": "params errror"})
            else:
                return JsonResponse({"errcode": "101", "errmsg": "params errror"})
        else:
            return JsonResponse({"errcode": "101", "errmsg": "params errror"})


class OrderLogsView(View):

    @method_decorator(admin_auth)
    @method_decorator(csrf_exempt)
    def get(self, request, user, order_no):
        """获取订单日志"""
        try:
            if order_no is not None:
                states_log = []
                states = OrderStatusLog.objects.filter(order_no=order_no)
                lena = len(states)
                sta_dic = {1: "Orderd", 2: "Payed", 3: "Delivering", 4: "Finished", 5: "Closed"}

                if lena > 0:
                    for state in states:
                        status = sta_dic.get(state.status)
                        if not state.is_admin:
                            try:
                                username = User.objects.get(id=state.user_id).username
                            except Exception as e:
                                management_logger.error(e)
                                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
                        else:
                            try:
                                username = Admin.objects.get(id=state.user_id).username
                            except Exception as e:
                                management_logger.error(e)
                                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
                        date = state.change_date.strftime("%Y-%m-%d %H:%M:%S")
                        state_log = {"status": status, "user": username, "date": date}
                        states_log.append(state_log)
                res = states_log
                return JsonResponse({"errcode": "0", "data": res})
            else:
                return JsonResponse({"errcode": "0", "data": '[]'})

        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
