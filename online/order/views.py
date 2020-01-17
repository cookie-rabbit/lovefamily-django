from django.db import transaction
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from paypal.standard.forms import PayPalPaymentsForm

from online.constants import PER_PAGE_GOODS_COUNT
from online.order.models import Order, Order_Goods, OrderAddress, OrderStatusLog
from online.goods.models import Goods, Image, Category
from management.user.models import User
from online.logger import online_logger
from utils.decorator import user_auth
from online.cart.models import Cart
from management.user.models import UserAddress
import management.user

import ast
import random
from datetime import datetime

from weigan_shopping import settings, env


# 【渲染】订单页面（地址）
class OrderAddressView(View):
    @method_decorator(user_auth)
    def get(self, request, user, res):
        carts_id = None
        goods_id = None
        goods_num = None
        order_no = None

        try:
            res = res.split(':')
            if res:
                if res[0] == "carts_id":
                    carts_id = res[1]
                elif res[0] == "goods_id":
                    goods_id = res[1].split("goods_num")[0]
                    goods_num = res[2]
                elif res[0] == "order_no":
                    order_no = res[1]
                else:
                    return JsonResponse({"errcode": "101", "errmsg": "Params error"})
            else:
                return JsonResponse({"errcode": "101", "errmsg": "Params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "Params error"})
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
                online_logger.error(e)
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
                        good_price = good_detail.on_price
                        good_description_en = good_detail.description_en
                        good_image = Image.objects.filter(goods_id=good_id)
                        total = total + quantity * good_price
                        good_dict.append(
                            {"id": good_id, "quantity": quantity, "name": good_name_en, "on_price": good_price,
                             "description": good_description_en,
                             "image": settings.URL_PREFIX + good_image[0].image.url})
                    except Exception as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": "102", "errmsg": "Db error"})

            elif goods_id is not None:
                if int(goods_num) > 0:
                    good_id = goods_id
                    quantity = int(goods_num)
                    try:
                        good_detail = Goods.objects.get(id=good_id)
                        good_name_en = good_detail.name_en
                        good_price = good_detail.on_price
                        good_description_en = good_detail.description_en
                        good_image = Image.objects.filter(goods_id=good_id)

                        total = total + quantity * good_price
                        good_dict.append(
                            {"id": good_id, "quantity": quantity, "name": good_name_en, "on_price": good_price,
                             "description": good_description_en,
                             "image": settings.URL_PREFIX + good_image[0].image.url})
                    except Exception as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": "102", "errmsg": "Db error"})
                else:
                    return JsonResponse({"errcode": "101", "errmsg": "the num is lower than 1"})

            elif order_no is not None:
                try:
                    order = Order.objects.filter(order_no=order_no)
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "can't find the order"})

                if len(order) > 0:
                    try:
                        goods = Order_Goods.objects.filter(order_id=order[0].id)
                    except Exception as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": "102", "errmsg": "Db error"})

                    for good in goods:
                        good_id = good.goods_id
                        quantity = good.quantity
                        good_name_en = good.name_en
                        good_price = good.on_price
                        good_description_en = good.description_en
                        good_image = str(good.img)
                        total = total + quantity * good_price
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
                    online_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "can't find the order"})

                if len(order) > 0:
                    order_status = order[0].status
                    res.update({"order_status": order_status})

            user = User.objects.get(id=user_id)
            orders = Order.objects.filter(user_id=user_id)
            order_quantity = len(orders)
            cart_quantity = request.session.get("%s_cart" % user_id, 0)

            res = {"user_info": user_info, "good_dict": good_dict, "total": total, "user": user,
                   "cart_quantity": cart_quantity, "order_quantity": order_quantity}

        return render(request, "myOrder.html", context=res)


# 订单列表详情
class OrdersDetailView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id

        order_no = request.GET.get('order_no')
        orders = Order.objects.filter(user_id=user_id)
        if len(orders) > 0:
            order = orders.get(order_no=order_no)
            if order != '':
                try:
                    goods = Order_Goods.objects.filter(order_id=order.id)
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": 102, "errmsg": "Db error"})
                if goods != '':
                    good_dic = []
                    for good in goods:
                        good_id = good.good
                        quantity = good.quantity
                        good_name_en = good.name_en
                        good_price = good.on_price
                        good_description_en = good.description_en
                        good_image = Image.objects.filter(goods_id=good.good)
                        good_dic.append(
                            {"good_id": good_id, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                             "description_en": good_description_en,
                             "image": settings.URL_PREFIX + good_image[0].image.url})
                    res = {"good_dic": good_dic, "order_no": order_no}
                    tpl = get_template("orderDetail.html")
                    result = tpl.render(res)
                    return JsonResponse({'errcode': 0, 'data': {"result": result}})
                else:
                    return JsonResponse({"errcode": 110, "errmsg": "goods not exist"})
            else:
                return JsonResponse({'errcode': 111, 'errmsg': "order not exist"})
        return JsonResponse({'errcode': 111, 'errmsg': "order not exist"})


# 【渲染】订单详情
class OrdersDetailsView(View):
    @method_decorator(user_auth)
    def get(self, request, user, order_no):
        user_id = user.id
        orders = Order.objects.filter(user_id=user_id)
        order_quantity = len(orders)
        cart_quantity = request.session.get("%s_cart" % user_id, 0)
        try:
            user_add = UserAddress.objects.get(user_id=user_id)
            name = user_add.name
            province = user_add.province
            city = user_add.city
            district = user_add.district
            road = user_add.road
            phone_number = user_add.phone_number
            postcode = user_add.postcode
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 102, "errmsg": "Db error"})

        user = User.objects.get(id=user_id)
        order_no = order_no
        orders = Order.objects.filter(user_id=user_id).filter(order_no=order_no)
        if len(orders) > 0:
            order = orders[0]
        else:
            order = None
        if order is not None:
            try:
                total = order.total
                goods = Order_Goods.objects.filter(order_id=order.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 102, "errmsg": "Db error"})
            if len(goods) > 0:
                good_dict = []
                for good in goods:
                    quantity = good.quantity
                    good_name_en = good.name_en
                    good_price = good.on_price
                    good_description_en = good.description_en
                    good_image = Image.objects.filter(goods_id=good.good)
                    good_dict.append({"id": good.good, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                                      "description_en": good_description_en,
                                      "image": settings.URL_PREFIX + good_image[0].image.url})
                user_info = {"name": name, "province": province, "city": city, "district": district,
                             "road": road, "phone_number": phone_number, "postcode": postcode}
                res = {"user_info": user_info, "good_dict": good_dict, "total": total, "user": user,
                       "cart_quantity": cart_quantity, "order_quantity": order_quantity}

                return render(request, "orderDetails.html", context=res)
            else:
                JsonResponse({"errcode": 101, "errmsg": "This order has no goods"})
        else:
            JsonResponse({"errcode": 101, "errmsg": "user_id is None"})


# 【渲染】订单列表
class OrdersListView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        status_query = request.GET.get('status', 0)

        orders = Order.objects.filter(user_id=user_id).order_by('-order_date')
        order_quantity = len(orders)
        try:
            status_query = int(status_query)
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 101, 'errmsg': "Params error"})
        try:
            order_no_first = ''
            if status_query == 0:
                orders_total = orders.order_by('-order_date')
            else:
                orders_total = orders.filter(status=status_query).order_by('-order_date')

            orders = orders_total[: PER_PAGE_GOODS_COUNT]

        except Exception as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 101, 'errmsg': "Params error"})
        order_count = orders_total.count()
        user = User.objects.get(id=user.id)

        if order_count > PER_PAGE_GOODS_COUNT:
            more = 'true'
        else:
            more = 'false'
        if len(orders) > 0:
            orders.count()
            if len(orders_total) > 0:
                order_no_first = orders_total[0].order_no
            order_dic = []
            good_dic = []
            is_null = 0

            for order in orders:
                order_no = order.order_no
                order_date = order.order_date
                total = order.total
                status = order.get_status_display()
                order_dic.append({"order_no": order_no, "order_date": order_date, "total": total, "status": status})

            try:
                order = orders.first()
                goods = Order_Goods.objects.filter(order_id=order.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 102, "errmsg": "Db error"})
            if goods != '':
                for good in goods:
                    quantity = good.quantity

                    good_name_en = good.name_en
                    good_price = good.on_price
                    good_description_en = good.description_en
                    good_image = Image.objects.filter(goods_id=good.good)
                    good_dic.append({"quantity": quantity, "name_en": good_name_en, "price": good_price,
                                     "description_en": good_description_en,
                                     "image": settings.URL_PREFIX + good_image[0].image.url})
            else:
                return JsonResponse({'errcode': 110, 'errmsg': "goods not exist"})
        else:
            order_dic = []
            good_dic = []
            is_null = 1

        category = []
        try:
            cates = Category.objects.filter(super_category__isnull=True)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        for cate in cates:
            try:
                sub_cates = Category.objects.filter(super_category__id=cate.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            if len(sub_cates) > 0:
                category.append({"id": cate.id, "name": cate.name,
                                 "sub_cates": [{'id': sub_cate.id, 'name': sub_cate.name} for sub_cate in sub_cates if
                                               sub_cates] if sub_cates else []})

        cart_quantity = request.session.get("%s_cart" % user_id)
        res = {"category": category, "order_dic": order_dic, "good_dic": good_dic, "status": status_query, "more": more,
               "order_no": order_no_first,
               "cart_quantity": cart_quantity, "order_quantity": order_quantity, "user": user, "is_null": is_null}
        return render(request, "myOrders.html", context=res)


class OrderCreateView(View):
    # 创建订单
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    @method_decorator(user_auth)
    def post(self, request, user):
        try:
            name = request.POST.get('name')
            province = request.POST.get('province')
            city = request.POST.get('city')
            district = request.POST.get('district')
            road = request.POST.get('road')
            postcode = request.POST.get('postcode')
            phone_number = request.POST.get('phone_number')
            goods = ast.literal_eval(request.POST.get('goods'))
            is_cart = request.POST.get('is_cart', 0)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 101, "errmsg": "params not all"})
        if len(goods) > 0:
            for good in goods:
                goods_id = good['good_id']
                good_count = good['good_count']
                count = int(good_count)
                good_list = Goods.objects.select_for_update().get(id=goods_id)
                if good_list.stock < count:
                    return JsonResponse(
                        {'errcode': 112, 'errmsg': "the {} stock is not enough".format(good_list.name_en)})

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

        save_id = transaction.savepoint()
        try:
            order_address = OrderAddress.objects.create(name=name, province=province, road=road,
                                                        city=city, district=district, postcode=postcode,
                                                        phone_number=phone_number)

            order = Order.objects.create(order_no=order_no, total=total, order_date=time, status=status,
                                         address=order_address, user=User.objects.get(id=user_id))
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 101, "errmsg": "Params error"})

        goods_ids = []
        for good in goods:
            goods_id = good['good_id']
            goods_ids.append(goods_id)
            good_count = good['good_count']
            try:
                Goodgoods = Goods.objects.select_for_update().get(id=goods_id)
            except Goods.DoesNotExist as e:
                transaction.savepoint_rollback(save_id)
                online_logger.error(e)
                return JsonResponse({'errcode': 110, 'errmsg': "goods not exist"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 102, 'errmsg': 'Db error'})
            count = int(good_count)

            if Goodgoods.stock < count:
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'errcode': 112, 'errmsg': "stock not enough"})

            name_en = Goodgoods.name_en
            on_price = Goodgoods.on_price
            description_en = Goodgoods.description_en

            good_img = Image.objects.filter(goods_id=goods_id)[0].image

            Goodgoods.actual_sale += count
            Goodgoods.stock -= count
            Goodgoods.save()
            total += good_count * Goodgoods.on_price

            Order_Goods.objects.create(order=order, good=goods_id, quantity=count, name_en=name_en, on_price=on_price,
                                       description_en=description_en, img=good_img)
            Order.objects.filter(id=order.id).update(total=total)

        time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        OrderStatusLog.objects.create(order_no=order_no, status=1, user_id=user_id, change_date=time)

        if is_cart == 1:
            try:
                Cart.objects.filter(goods_id__in=goods_ids).delete()
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 102, 'errmsg': 'Db error'})

        href = "http://10.168.2.111:8000/orders/{order_no}/pay/".format(order_no=order.order_no)
        return JsonResponse({"errcode": 0, "data": {"result": "ordered success", "href": href}})

    # 翻页
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = request.session.get("user_id", None)
        offset = request.GET.get('offset', 0)
        status_query = request.GET.get('status', 0)

        try:
            offset = int(offset)
            status_query = int(status_query)
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 101, 'errmsg': "Params error"})
        try:
            if status_query == 0:
                orders_total = Order.objects.filter(user_id=user_id).order_by('-order_date')
            else:
                orders_total = Order.objects.filter(user_id=user_id, status=status_query).order_by('-order_date')
            orders = orders_total[offset:offset + PER_PAGE_GOODS_COUNT]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 102, 'errmsg': "Db error"})

        if orders.count() > offset + PER_PAGE_GOODS_COUNT:
            more = 'true'
        else:
            more = 'false'
        if orders.count() > 0:
            order_dic = []

            for order in orders:
                order_no = order.order_no
                order_date = order.order_date
                total = order.total
                status = order.get_status_display()
                order_dic.append({"order_no": order_no, "order_date": order_date, "total": total, "status": status})
        else:
            order_dic = []
        res_order = {"order_dic": order_dic}
        tpl = get_template("orderBlock.html")
        res = tpl.render(res_order)
        return JsonResponse({"errcode": 0, "data": {"result": res, "more": more}})


# 下单页面用户地址修改
class UserAddressView(View):
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    @method_decorator(user_auth)
    def post(self, request, user):
        user_id = user.id
        try:
            name = request.POST.get('name')
            province = request.POST.get('province')
            city = request.POST.get('city')
            district = request.POST.get('district')
            road = request.POST.get('road')
            postcode = request.POST.get('postcode')
            phone_number = request.POST.get('phone_number')
            if not (name or road or district or city or province or phone_number or postcode):
                return JsonResponse({"errcode": 101, "errmsg": "Please full fill the content"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 101, "errmsg": "params not all"})
        try:
            useraddress = UserAddress.objects.get(user_id=user_id)
            useraddress.name = name
            useraddress.province = province
            useraddress.city = city
            useraddress.district = district
            useraddress.road = road
            useraddress.phone_number = phone_number
            useraddress.postcode = postcode
            useraddress.save()
            return JsonResponse({"errcode": 0, "errmsg": "updated success"})
        except management.user.models.UserAddress.DoesNotExist:
            try:
                UserAddress.objects.create(user_id=user_id, name=name, province=province, road=road,
                                           city=city, district=district, postcode=postcode, phone_number=phone_number)
                return JsonResponse({"errcode": 0, "data": "created success"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 102, "errmsg": "Db error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 102, "errmsg": "Db error"})


# paypal支付按钮渲染
class PayView(View):
    def __init__(self, request, order_no, total, **kwargs):
        super().__init__(**kwargs)
        self.request = request
        self.order_no = order_no
        self.total = total

    def pay(self):
        paypal_dict = {
            "business": settings.PAYMENT_BUSSINESS,
            "amount": self.total,
            "item_name": settings.PAYMENT_ITEM,
            "invoice": self.order_no,
            "notify_url": settings.PAYMENT_NOTIFY_URL,
            "return": settings.ONLINE_PAYMENT_RETURN_URL,
            "cancel_return": settings.ONLINE_PAYMENT_CANCEL_URL + self.order_no + '/pay/',
            "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        context = {"form": form}
        return render(self.request, "testPay.html", context=context)


# 【渲染】订单页面（地址）
class OrderPayView(View):
    @method_decorator(user_auth)
    def get(self, request, user, order_no):

        try:
            user_id = user.id

            orders = Order.objects.filter(user_id=user_id).order_by('-order_date')
            order_quantity = len(orders)
            orders = Order.objects.filter(order_no=order_no)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 102, "errmsg": "Db error"})

        if len(orders) > 0:
            order = orders[0]
            total = order.total
            if order.status in [2, 3, 4]:
                return JsonResponse({"errcode": 101, "errmsg": "The order has been payed"})
            if order.status == 5:
                return JsonResponse({"errcode": 101, "errmsg": "The order has been closed"})
        else:
            return JsonResponse({"errcode": 102, "errmsg": "Can't find the order"})
        if order.user_id != user.id:
            return JsonResponse({"errcode": 101, "errmsg": "This is not your order"})

        a = PayView(request, order_no, total)
        b = a.pay().content
        a = str(b).replace("\r", "").replace("\\n", "").replace("b'", "").replace("\'", "")

        user = User.objects.get(id=user.id)
        cart_quantity = request.session.get("%s_cart" % user_id)

        context = {"total": total, "content": a, "order_quantity": order_quantity, "user": user,
                   "cart_quantity": cart_quantity}
        return render(request, "payOrder.html", context=context)


# 【渲染】支付成功
class PaySuccessView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        try:
            user_id = user.id
            orders = Order.objects.filter(user_id=user_id).order_by('-order_date')
            order_quantity = len(orders)
            user = User.objects.get(id=user.id)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 102, "errmsg": "Db error"})
        cart_quantity = request.session.get("%s_cart" % user_id)
        context = {"order_quantity": order_quantity, "user": user, "cart_quantity": cart_quantity,
                   "index": env.ONLINE_URL, "order_href": env.ONLINE_URL + 'orders/'}
        return render(request, "paySucess.html", context=context)
