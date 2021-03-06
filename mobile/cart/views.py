import json
from django.http import JsonResponse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from management.user.models import User
from online.cart.models import Cart
from online.goods.models import Goods, Image, Category
from mobile.logger import mobile_logger
from utils.decorator import user_auth
from weigan_shopping import settings


class CartsView(View):
    """ 获取购物车列表"""

    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "can not find user in db"})
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            cart_quantity = request.session.get("%s_cart" % user_id)
            if cart_quantity:
                try:
                    carts = Cart.objects.filter(user__id=user_id)
                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "Db error"})
                cart_list = []
                sum = 0
                for cart in carts:
                    sum += cart.quantity * cart.goods.on_price
                    image = Image.objects.filter(goods=cart.goods)
                    origin_price = float(cart.goods.origin_price)
                    origin_price = ("%.2f" % origin_price)
                    origin_price = float(origin_price)
                    on_price = float(cart.goods.on_price)
                    on_price = ("%.2f" % on_price)
                    on_price = float(on_price)
                    cart_list.append({"id": cart.id, "goods_id": cart.goods.id, "name": cart.goods.name_en,
                                      "description": cart.goods.description_en, "price": origin_price,
                                      "on_price": on_price,
                                      "image": settings.URL_PREFIX + image[0].image.url, "quantity": cart.quantity})
                    request.session['%s_cart' % user.id] += cart.quantity
                data = {"carts_list": cart_list, "cart_quantity": cart_quantity, "sum": sum}
            else:
                data = {"carts_list": [], "cart_quantity": 0, "sum": 0}
        else:
            data = {"carts_list": "", "cart_quantity": 0, "sum": 0}
        return JsonResponse({"errcode": "0", "data": data})

    """新增到购物车"""

    @method_decorator(user_auth)
    def post(self, request, user):
        data = json.loads(request.body.decode())
        goods_id = data.get("goods_id", None)
        quantity = data.get("quantity", 1)
        if not goods_id:
            return JsonResponse({"errcode": "101", "errmsg": "Empty params"})
        try:
            goods_id = int(goods_id)
            quantity = int(quantity)
            single_goods = Goods.objects.get(id=goods_id)
        except ValueError as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "Params error"})
        except Goods.DoesNotExist as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Can not find goods in "})
        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        try:
            carts = Cart.objects.filter(user=user, goods=single_goods)
            if carts:
                cart = carts[0]
                cart.quantity = cart.quantity + quantity
                cart.save()
            else:
                cart = Cart.objects.create(user=user, quantity=quantity, goods=single_goods)
        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        request.session["%s_cart" % user.id] += quantity
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse(
            {"errcode": "0", "errmsg": "Added to cart", "data": {"quantity": total_quantity}})


class CartView(View):
    """修改购物车指定条目"""

    @method_decorator(user_auth)
    def put(self, request, user, cart_id):
        data = json.loads(request.body.decode())
        quantity = data.get("quantity", None)
        if quantity is None:
            return JsonResponse({"errcode": "101", "errmsg": "params not all"})
        try:
            quantity = int(quantity)
            cart = Cart.objects.get(id=cart_id)
            before_quantity = cart.quantity
            cart.quantity = quantity
            cart.save()
        except Cart.DoesNotExist as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Can not find goods in "})
        except ValueError as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "Params error"})
        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        carts = Cart.objects.filter(user_id=user)
        num = 0
        for cart in carts:
            num += cart.quantity
        request.session['%s_cart' % user.id] = num
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse({"errcode": "0", "errmsg": "update success", "data": {"quantity": total_quantity}})

    """删除购物车指定条目"""

    @method_decorator(user_auth)
    def delete(self, request, user, cart_id):
        try:
            cart_id = int(cart_id)
            cart = Cart.objects.get(id=cart_id)
            cart.delete()
        except ValueError as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "Params error"})
        except Exception as e:
            mobile_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        request.session["%s_cart" % user.id] -= cart.quantity
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse({"errcode": "0", "errmsg": "delete success", "data": {"quantity": total_quantity}})
