import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from management.user.models import User
from online.cart.models import Cart
from online.goods.models import Goods
from online.logger import online_logger
from utils.decorator import user_auth
from weigan_shopping import settings


class CartsView(View):

    def get(self,request):
        user_id = request.session.get("user_id", None)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "can not find user in db"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            quantity = request.session.get("%s_cart" % user_id)
            if quantity:
                try:
                    carts = Cart.objects.filter(user__id=user_id)
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "db error"})
                cart_list = [{"id":cart.id,"name":cart.goods.name_en,"description":cart.goods.description_en,"price":cart.goods.price,"image":settings.URL_PREFIX+cart.goods.image.url} for cart in carts]
                context = {"user":user.username,"carts_list":cart_list,"quantity":quantity}
            else:
                context = {"user":user.username}
        else:
            context = {}
        print(context)
        return JsonResponse(context,safe=False)
        # return render(request,"mycart.html",context=context)

    @method_decorator(user_auth)
    def post(self,request,user):
        data = json.loads(request.body.decode())
        goods_id = data.get("goods_id",None)
        quantity = data.get("quantity",1)
        if not goods_id:
            return JsonResponse({"errcode":"101","errmsg":"empty params"})
        try:
            goods_id = int(goods_id)
            quantity = int(quantity)
            single_goods = Goods.objects.get(id=goods_id)
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"101","errmsg":"params error"})
        except Goods.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"can not find goods in db"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        try:
            carts = Cart.objects.filter(user=user, goods=single_goods)
            if carts:
                cart = carts[0]
                cart.quantity = cart.quantity + quantity
                cart.save()
            else:
                cart = Cart.objects.create(user=user, quantity=quantity, goods=single_goods)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        request.session["%s_cart" % user.id] += quantity
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse({"errcode":"0","errmsg":"add to cart success","data":{"quantity":str(total_quantity)}})


class CartView(View):
    @method_decorator(user_auth)
    def put(self,request,user,cart_id):
        data = json.loads(request.body.decode())
        quantity = data.get("quantity",None)
        if quantity is None:
            return JsonResponse({"errcode":"101","errmsg":"params not all"})
        try:
            quantity = int(quantity)
            cart = Cart.objects.get(id=cart_id)
            before_quantity = cart.quantity
            cart.quantity = quantity
            cart.save()
        except Cart.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"can not find goods in db"})
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"101","errmsg":"params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        sub_quantity = quantity - before_quantity
        request.session['%s_cart' % user.id] += sub_quantity
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse({"errcode":"0","errmsg":"update success","data":{"quantity":total_quantity}})

    @method_decorator(user_auth)
    def delete(self, request, user, cart_id):
        try:
            cart_id = int(cart_id)
            cart = Cart.objects.get(id=cart_id)
            cart.delete()
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        request.session["%s_cart" % user.id] -= cart.quantity
        total_quantity = request.session["%s_cart" % user.id]
        return JsonResponse({"errcode": "0", "errmsg": "delete success","data":{"quantity":total_quantity}})