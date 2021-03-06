from datetime import timedelta

from django.db import transaction
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from mobile.card.views import PaymentView
from online.constants import PER_PAGE_GOODS_COUNT
from online.order.models import Order, Order_Goods, OrderAddress, OrderStatusLog
from online.goods.models import Goods, Image
from management.user.models import User
from mobile.logger import mobile_logger
from utils.decorator import user_auth
from online.cart.models import Cart
from management.user.models import UserAddress
import management.user
from weigan_shopping import settings

import random
import json


# 获取订单信息及地址
class OrderAddressView(View):
    @method_decorator(user_auth)
    def post(self, request, user):
        data = json.loads(request.body.decode())
        carts_id = data.get('carts_id', None)
        goods_id = data.get('goods_id', None)
        goods_num = data.get('goods_num', 0)
        order_no = data.get('order_no', None)
        user_id = user.id
        good_dict = []
        total = 0
        if user_id:
            try:
                user = UserAddress.objects.get(user_id=user_id)
                name = user.name
                province = user.province
                city = user.city
                district = user.district
                road = user.road
                phone_number = user.phone_number
                postcode = user.postcode
                is_null = 0
            except management.user.models.UserAddress.DoesNotExist:
                name = ''
                province = ''
                city = ''
                district = ''
                road = ''
                phone_number = ''
                postcode = ''
                is_null = 1
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})

            if carts_id is not None:
                carts_id = carts_id.split(",")
                carts = Cart.objects.filter(id__in=carts_id).filter(user_id=user_id)
                for cart in carts:
                    good_id = cart.goods_id
                    quantity = cart.quantity
                    try:
                        good_detail = Goods.objects.get(id=good_id)
                        good_name_en = good_detail.name_en
                        good_price = float(good_detail.on_price)
                        good_price = ("%.2f" % good_price)
                        good_price = float(good_price)
                        good_description_en = good_detail.description_en
                        good_image = Image.objects.filter(goods_id=good_id)
                        total = total + quantity * good_price
                        total = ("%.2f" % total)
                        total = float(total)
                        good_dict.append(
                            {"id": good_id, "quantity": quantity, "name": good_name_en, "on_price": good_price,
                             "description": good_description_en,
                             "image": settings.URL_PREFIX + good_image[0].image.url})
                    except Exception as e:
                        mobile_logger.error(e)
                        return JsonResponse({"errcode": "102", "errmsg": "Db error"})

            elif goods_id is not None:
                if int(goods_num) > 0:
                    good_id = goods_id
                    quantity = int(goods_num)
                    try:
                        good_detail = Goods.objects.get(id=good_id)
                        good_name_en = good_detail.name_en
                        good_price = float(good_detail.on_price)
                        good_price = ("%.2f" % good_price)
                        good_price = float(good_price)
                        good_description_en = good_detail.description_en
                        good_image = Image.objects.filter(goods_id=good_id)

                        total = total + quantity * good_price
                        total = ("%.2f" % total)
                        total = float(total)
                        good_dict.append(
                            {"id": good_id, "quantity": quantity, "name": good_name_en, "on_price": good_price,
                             "description": good_description_en,
                             "image": settings.URL_PREFIX + good_image[0].image.url})
                    except Exception as e:
                        mobile_logger.error(e)
                        return JsonResponse({"errcode": "102", "errmsg": "Db error"})
                else:
                    return JsonResponse({"errcode": "101", "errmsg": "the num is lower than 1"})

            elif order_no is not None:
                try:
                    order = Order.objects.filter(order_no=order_no)
                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "can't find the order"})

                if len(order) > 0:
                    try:
                        goods = Order_Goods.objects.filter(order_id=order[0].id)
                    except Exception as e:
                        mobile_logger.error(e)
                        return JsonResponse({"errcode": "102", "errmsg": "Db error"})

                    for good in goods:
                        good_id = good.good
                        quantity = good.quantity
                        good_name_en = good.name_en
                        good_price = float(good.on_price)
                        good_price = ("%.2f" % good_price)
                        good_price = float(good_price)
                        good_description_en = good.description_en
                        good_image = str(good.img)
                        total = total + quantity * good_price
                        total = ("%.2f" % total)
                        total = float(total)
                        good_dict.append(
                            {"id": good_id, "quantity": quantity, "name": good_name_en, "on_price": good_price,
                             "description": good_description_en,
                             "image": settings.URL_PREFIX + '/media/' + good_image})
            else:
                good_dict = []
                total = 0

            user_info = {"name": name, "province": province, "city": city, "district": district,
                         "road": road, "phone_number": phone_number, "postcode": postcode, "is_null": is_null}
            res = {"user_info": user_info, "good_dict": good_dict, "total": total}
            if order_no:
                try:
                    order = Order.objects.filter(order_no=order_no)
                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "can't find the order"})

                if len(order) > 0:
                    order_status = order[0].status
                    res.update({"order_status": order_status})

            return JsonResponse({"errcode": "0", "data": res})

        else:
            JsonResponse({"errcode": "101", "errmsg": "user_id is None"})


# 获取订单详情
class OrdersDetailView(View):
    @method_decorator(user_auth)
    def get(self, request, user, order_no):
        user_id = user.id
        order_no = order_no
        orders = Order.objects.filter(user_id=user_id)
        order = orders.get(order_no=order_no)
        total = 0
        if order != '':
            try:
                goods = Order_Goods.objects.filter(order_id=order.id)
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": 102, "errmsg": "Db error"})

            if goods != '':
                good_dic = []
                for good in goods:
                    quantity = good.quantity
                    good_name_en = good.name_en
                    good_price = float(good.on_price)
                    good_price = ("%.2f" % good_price)
                    good_price = float(good_price)
                    good_description_en = good.description_en
                    good_image = str(good.img)
                    total += good_price * quantity
                    total = ("%.2f" % total)
                    total = float(total)
                    good_dic.append({"quantity": quantity, "name": good_name_en, "price": good_price,
                                     "description": good_description_en,
                                     "image": settings.URL_PREFIX + '/media/' + good_image})
                item = good_dic
                data = {"item": item, "total": total}
                return JsonResponse({'errcode': "0", 'data': data})

            else:
                return JsonResponse({"errcode": "110", "errmsg": "goods not exist"})

        else:
            return JsonResponse({'errcode': "111", 'errmsg': "order not exist"})


# 订单列表，创建订单
class OrdersView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        status_query = request.GET.get('status', 0)
        offset = int(request.GET.get('offset', 0))

        orders = Order.objects.filter(user_id=user_id).order_by('-order_date')
        try:
            status_query = int(status_query)
        except ValueError as e:
            mobile_logger.error(e)
            return JsonResponse({'errcode': 101, 'errmsg': "Params error"})
        try:
            if status_query == 0:
                orders_total = orders.order_by('-order_date')
            else:
                orders_total = orders.filter(status=status_query).order_by('-order_date')
            orders = orders_total[offset: offset + PER_PAGE_GOODS_COUNT]

        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({'errcode': 101, 'errmsg': "Params error"})
        order_count = orders_total.count()

        if order_count > PER_PAGE_GOODS_COUNT + offset:
            more = 'true'
        else:
            more = 'false'
        if orders.count() > 0:
            order_dic = []

            for order in orders:
                order_no = order.order_no
                order_date = order.order_date.strftime("%Y-%m-%d %H:%M:%S")
                exc = timezone.now() - order.order_date
                set_hour = timedelta(hours=3)
                exc = (exc - set_hour).total_seconds()
                if exc > 0:
                    order_chg = Order.objects.filter(order_no=order_no)
                    if len(order_chg) > 0:
                        if int(order.status) == 1:
                            order.status = 5
                            order.save()
                total = order.total
                status = order.get_status_display()
                order_dic.append({"order_no": order_no, "order_date": order_date, "total": total, "status": status})
        else:
            order_dic = []

        data = {"order_dic": order_dic, "status": status_query, "more": more}
        return JsonResponse({'errcode': "0", 'data': data})

    '''创建订单'''

    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    @method_decorator(user_auth)
    def post(self, request, user):
        try:
            data = json.loads(request.body.decode())
            user_add = UserAddress.objects.get(user_id=user.id)
            name = user_add.name
            province = user_add.province
            city = user_add.city
            district = user_add.district
            road = user_add.road
            postcode = user_add.postcode
            phone_number = user_add.phone_number
            goods = data.get('goods')
            is_cart = data.get('is_cart', 0)
        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": 101, "errmsg": "params not all"})
        if len(goods) > 0:
            for good in goods:
                goods_id = good['good_id']
                good_count = good['good_count']
                count = int(good_count)
                good_list = Goods.objects.select_for_update().get(id=goods_id)
                # if good_list.stock < count:
                #     return JsonResponse({'errcode': 112, 'errmsg': "the {} stock is not enough".format(good_list.name_en)})

            user_id = user.id
            time = timezone.now()
            i = timezone.now()
            month = str(i.month)
            day = str(i.day)
            hour = str(i.hour)
            minute = str(i.minute)
            second = str(i.second)
            if len(month) < 2:
                month = '0' + month
            if len(day) < 2:
                day = '0' + day
            if len(hour) < 2:
                hour = '0' + hour
            if len(minute) < 2:
                minute = '0' + minute
            if len(second) < 2:
                second = '0' + second

            order_no = "0000" + str(i.year) + month + day + hour + minute + second + str(random.randint(0000, 9999))
            status = 1
            total = 0
            try:
                order_address = OrderAddress.objects.create(name=name, province=province, road=road,
                                                            city=city, district=district, postcode=postcode,
                                                            phone_number=phone_number)

                order = Order.objects.create(order_no=order_no, total=total, order_date=time, status=status,
                                             address=order_address, user=User.objects.get(id=user_id))
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": 101, "errmsg": "Params error"})

            goods_ids = []
            for good in goods:
                try:
                    goods_id = good['good_id']
                    goods_ids.append(goods_id)
                    good_count = good['good_count']
                    good_list = Goods.objects.select_for_update().get(id=goods_id)
                except Goods.DoesNotExist as e:
                    mobile_logger.error(e)
                    return JsonResponse({'errcode': 110, 'errmsg': "Goods not exist"})

                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({'errcode': 102, 'errmsg': 'Db error'})

                count = int(good_count)

                try:
                    name_en = good_list.name_en
                    on_price = good_list.on_price
                    description_en = good_list.description_en
                    good_img = Image.objects.filter(goods_id=goods_id)[0].image
                    good_list.actual_sale += count
                    good_list.stock -= count
                    good_list.save()
                    total += int(good_count) * good_list.on_price
                    total = ("%.2f" % total)
                    total = float(total)
                    Order_Goods.objects.create(good=goods_id, order=order, quantity=count, name_en=name_en,
                                               on_price=on_price,
                                               description_en=description_en, img=good_img)
                    Order.objects.filter(id=order.id).update(total=total)
                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({'errcode': 102, 'errmsg': 'Db error'})

            try:
                time = timezone.now()
                OrderStatusLog.objects.create(order_no=order_no, status=1, user_id=user_id, change_date=time)
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({'errcode': 102, 'errmsg': 'Db error'})

            if is_cart == 1:
                try:
                    Cart.objects.filter(goods_id__in=goods_ids).delete()
                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({'errcode': 102, 'errmsg': 'Db error'})

            data = {"order_no": order_no}
            return JsonResponse({"errcode": 0, "errmsg": "ordered success", "data": data})
        else:
            return JsonResponse({"errcode": 101, "errmsg": "There's no goods"})


# 下单页面用户地址修改
class UserAddressView(View):
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    @method_decorator(user_auth)
    def post(self, request, user):
        user_id = user.id
        try:
            data = json.loads(request.body.decode())
            name = data.get('name')
            province = data.get('province')
            city = data.get('city')
            district = data.get('district')
            road = data.get('road')
            postcode = data.get('postcode')
            phone_number = data.get('phone_number')
        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": 101, "errmsg": "params not all"})
        try:
            UserAddress.objects.filter(user_id=user_id).update(name=name, province=province, road=road,
                                                               city=city, district=district, postcode=postcode,
                                                               phone_number=phone_number)
            return JsonResponse({"errcode": 0, "errmsg": "updated success"})

        except management.user.models.UserAddress.DoesNotExist:
            try:
                UserAddress.objects.create(user_id=user_id, name=name, province=province, road=road,
                                           city=city, district=district, postcode=postcode, phone_number=phone_number)
                return JsonResponse({"errcode": 0, "data": "created success"})

            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": 102, "errmsg": "Db error"})

        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": 102, "errmsg": "Db error"})


# 提交支付
class PayView(View):
    def get(self, request, order_no):
        try:
            goods = Order.objects.filter(order_no=order_no)
        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": 102, "errmsg": "Db error"})

        if len(goods) > 0:
            goods = goods[0]
            total = goods.total
        else:
            return JsonResponse({"errcode": 102, "errmsg": "can't find the order"})

        a = PaymentView(request, order_no, total)
        b = a.pay().content
        a = str(b).replace("\r", "").replace("\\n", "").replace("b'", "").replace("\'", "")

        data = {"total": total, "content": a}
        return JsonResponse({"errcode": 0, "data": data})

