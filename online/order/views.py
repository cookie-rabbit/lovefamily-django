from django.db import transaction
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from online.logger import online_logger
from utils.decorator import user_auth
from online.order.models import Order, Order_Goods, OrderAddress
from online.goods.models import Goods
from management.user.models import User
import random
from django.http import JsonResponse
from django.http import QueryDict
import ast
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
import json

# 【渲染】订单列表
@csrf_exempt
@user_auth
def orders_list(request, user):
    user_id = user.id
    orders = Order.objects.filter(user_id=user_id)
    if orders != '':
        order_dic = []
        for order in orders:
            order_no = order.order_no
            order_date = order.order_date
            total = order.total
            status = order.status
            order_dic.append({"order_no": order_no, "order_date": order_date, "total": total, "status": status})

        order_last = orders.last()
        try:
            goods = Order_Goods.objects.filter(order_id=order_last.id)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"res": 111, "errmsg": "数据库错误"})
        if goods != '':
            good_dic = []
            for good in goods:
                good_id = good.goods_id
                quantity = good.quantity
                good_detail = Goods.objects.get(id=good_id)
                good_name_en = good_detail.name_en
                good_price = good_detail.price
                good_description_en = good_detail.description_en
                good_image = str(good_detail.image)
                good_dic.append({"quantity": quantity, "good_name_en": good_name_en, "good_price": good_price,
                                 "good_description_en": good_description_en, "good_image": good_image})
            res = {"order_dic": order_dic, "good_dic": good_dic}
            tpl = get_template("myOrders.html")
            res = tpl.render(res)
            return JsonResponse({'errcode': 0, 'data': res})

    return JsonResponse({'errcode': 4, 'data': "请求方式错误"})


# 创建订单/订单搜索与订单列表接口
@csrf_exempt
@user_auth
@transaction.atomic
def order_generate(request, user):
    if request.method == 'POST':
        if request.POST:
            try:
                name = request.POST.get('name')
                address_line_1 = request.POST.get('address_line1')
                address_line_2 = request.POST.get('address_line2')
                city = request.POST.get('city')
                state = request.POST.get('state')
                zip = request.POST.get('zip')
                phone = request.POST.get('phone')
                goods = ast.literal_eval(request.POST.get('goods'))
                user_id = request.POST.get('user_id')
                total = request.POST.get('total')
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"res": 10, "errmsg": "订单信息不完整"})
            else:
                if phone.isdigit() and user_id.isdigit() and total.isdigit():
                    time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d")
                    order_no = random.randint(0, 9999999999)

                    save_id = transaction.savepoint()
                    order_address = OrderAddress.objects.create(name=name, address_line_1=address_line_1,
                                                                address_line_2=address_line_2,
                                                                city=city, district=state, postcode=zip,
                                                                phone=phone)

                    order = Order.objects.create(order_no=order_no, total=total, order_date=time, status=3,
                                                 address=order_address, user=User.objects.get(id=user_id))

                    for good in goods:
                        goods_id = good['good_id']
                        good_count = good['good_count']
                        try:
                            Goodgoods = Goods.objects.select_for_update().get(id=goods_id)
                        except Goods.DoesNotExist as e:
                            transaction.savepoint_rollback(save_id)
                            online_logger.error(e)
                            return JsonResponse({'res': 2, 'errmsg': '商品信息错误'})
                        except Exception as e:
                            online_logger.error(e)
                            return JsonResponse({'res': 2, 'errmsg': '数据库错误'})
                        count = int(good_count)

                        if Goodgoods.stock < count:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'res': 4, 'errmsg': '库存不足'})

                        Goodgoods.sale += count
                        Goodgoods.stock -= count
                        Goodgoods.save()

                        goods = Goods.objects.select_for_update().get(id=goods_id)
                        # order = Order.objects.get(order_no=order_no)
                        Order_Goods.objects.create(order=order, goods=goods, quantity=count)

                    return JsonResponse({"res": 5, "errmsg": "订单创建成功"})
                else:
                    return JsonResponse({"res": 9, "errmsg": "订单信息格式不正确"})
    if request.method == 'GET':
        user_id = user.id
        offset = request.GET.get('offset')
        status = request.GET.get('status')
        peroid = request.GET.get('peroid')
        order_no = request.GET.get('order_no')

        orders = Order.objects.filter(user_id=user_id)

        if status and peroid and order_no is None and offset:
            orders = orders
        elif (offset and peroid and order_no) is None and status:
            orders = orders.filter(status=status)
        elif (offset and status and order_no) is None and peroid:
            date_time = peroid.split('-')
            try:
                start_date = datetime.strptime(date_time[0], '%Y/%m/%d').strftime('%Y-%m-%d')
                end_date = datetime.strptime(date_time[1], '%Y/%m/%d').strftime('%Y-%m-%d')
                # if abs(end_date - start_date) < timedelta(days=1):
                orders = orders.filter(order_date__range=(start_date, end_date))
            except ValueError as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 1, 'data': "日期非法"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 2, 'data': "日期格式不正确"})

        elif (offset and status and peroid) is None and order_no:
            orders = orders.filter(order_no=order_no)
        elif (offset and status and peroid and order_no) is None:
            orders = orders
        else:
            return JsonResponse({'errcode': 4, 'data': "查询条件过多"})

        if orders != '':
            order_dic = []
            for order in orders:
                order_no = order.order_no
                order_date = order.order_date
                total = order.total
                status = order.status
                aaa = {"order_no": order_no, "order_date": order_date, "total": total, "status": status}
                order_dic.append(aaa)

            return JsonResponse({'errcode': 0, 'data': order_dic})
        return JsonResponse({'errcode': 4, 'data': "无订单"})
    else:
        return JsonResponse({"res": 6, "errmsg": "请求方式错误"})


# 修改订单状态
@csrf_exempt
@transaction.atomic
def oder_status_change(request):
    if request.method == 'PUT':
        if request.body:
            try:
                put = QueryDict(request.body)
                order_no = put.get('order_no')
                status = put.get('status')
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"res": 111, "errmsg": "请求数据不全或格式错误"})
            if status.isdigit() and order_no.isdigit():

                try:
                    order = Order.objects.get(order_no=order_no)
                except Order.DoesNotExist as e:
                    online_logger.error(e)
                    return JsonResponse({"res": 111, "errmsg": "订单不存在"})
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"res": 111, "errmsg": "数据库错误"})

                else:
                    if order.status == 2:
                        return JsonResponse({"res": 222, "errmsg": "订单已完成，不能修改状态"})
                    order = Order.objects.get(order_no=order_no)
                    order.status = status
                    order.save()
                    return JsonResponse({"res": 5, "errmsg": "订单状态修改成功"})
            else:
                return JsonResponse({"res": 8, "errmsg": "订单状态或订单号不正确"})
        else:
            return JsonResponse({"res": 7, "errmsg": "未收到请求内容或请求方式错误"})
    else:
        return JsonResponse({"res": 6, "errmsg": "请求方式错误"})
