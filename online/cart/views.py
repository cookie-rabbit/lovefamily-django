import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from management.user.models import User
from online.cart.models import Cart
from online.goods.models import Goods, Image, Category
from online.logger import online_logger
from online.order.models import Order
from utils.decorator import user_auth
from weigan_shopping import settings


class CartsView(View):
    """获取购物车列表"""

    @method_decorator(csrf_exempt)
    def get(self, request):
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

        user_id = request.session.get("user_id", None)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                orders = Order.objects.filter(user=user)
                order_quantity = len(orders)
            except User.DoesNotExist as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "can not find user in db"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            cart_quantity = request.session.get("%s_cart" % user_id)
            if cart_quantity:
                try:
                    carts = Cart.objects.filter(user__id=user_id)
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "Db error"})
                cart_list = []
                sum = 0
                for cart in carts:
                    sum += cart.quantity * cart.goods.on_price
                    image = Image.objects.filter(goods=cart.goods)
                    cart_list.append({"id": cart.id, "goods_id": cart.goods.id, "name": cart.goods.name_en,
                                      "description": cart.goods.description_en, "price": cart.goods.on_price,
                                      "image": settings.URL_PREFIX + image[0].image.url, "quantity": cart.quantity})
                context = {"user": user, "carts_list": cart_list, "cart_quantity": cart_quantity,
                           "order_quantity": order_quantity, "sum": sum, "category": category}
            else:
                context = {"user": user, "cart_quantity": 0, "order_quantity": order_quantity, "sum": 0,
                           "category": category}
        else:
            context = {"sum": 0, "category": category}
        aaa = request.META['REMOTE_ADDR']
        # return JsonResponse(context,safe=False)
        return render(request, "myCart.html", context=context)

    @method_decorator(user_auth)
    @method_decorator(csrf_exempt)
    def post(self, request, user):
        goods_id = request.POST.get("goods_id", None)
        quantity = request.POST.get("quantity", 1)
        if not goods_id:
            return JsonResponse({"errcode": "101", "errmsg": "Empty params"})
        try:
            goods_id = int(goods_id)
            quantity = int(quantity)
            single_goods = Goods.objects.get(id=goods_id)
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "Params error"})
        except Goods.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Can not find goods in "})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        try:
            carts = Cart.objects.filter(user=user, goods=single_goods)
            if carts:
                cart = carts[0]
                cart.quantity = cart.quantity + quantity
                cart.save()
            else:
                Cart.objects.create(user=user, quantity=quantity, goods=single_goods)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        request.session["%s_cart" % user.id] += quantity
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse(
            {"errcode": "0", "errmsg": "add to cart success", "data": {"quantity": str(total_quantity)}})


class CartView(View):
    @method_decorator(user_auth)
    def post(self, request, user, cart_id):
        quantity = request.POST.get("quantity", None)
        if quantity is None:
            return JsonResponse({"errcode": "101", "errmsg": "params not all"})
        try:
            quantity = int(quantity)
            cart = Cart.objects.get(id=cart_id)
            before_quantity = cart.quantity
            cart.quantity = quantity
            cart.save()
        except Cart.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Can not find goods in "})
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "Params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        sub_quantity = quantity - before_quantity
        request.session['%s_cart' % user.id] += sub_quantity
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse({"errcode": "0", "errmsg": "update success", "data": {"quantity": total_quantity}})

    @method_decorator(user_auth)
    def delete(self, request, user, cart_id):
        try:
            cart_id = int(cart_id)
            cart = Cart.objects.get(id=cart_id)
            cart.delete()
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "Params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        request.session["%s_cart" % user.id] -= cart.quantity
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse({"errcode": "0", "errmsg": "delete success", "data": {"quantity": total_quantity}})
