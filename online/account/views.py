import re

from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from management.user.models import User, UserAddress
from online.cart.models import Cart
from online.goods.models import Category
from online.logger import online_logger
from online.order.models import Order
from utils.decorator import user_auth
from weigan_shopping import settings


class LoginView(View):
    """用户登录"""
    def post(self, request):
        username = request.POST.get("name", None)
        print(username)
        password = request.POST.get("password", None)
        print(password)
        if not all([username, password]):
            return JsonResponse({"errcode": "101", "errmsg": "params not all"})
        try:
            user = User.objects.filter(Q(email=username) | Q(phone=username))
            if user:
                user = user[0]
            else:
                return JsonResponse({"errcode": "105", "errmsg": "please login after sign up"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        if not user.check_password(password):
            return JsonResponse({"errcode": "104", "errmsg": "password error"})
        try:
            carts = Cart.objects.filter(user__id=user.id)
            quantity = [cart.quantity for cart in carts]
            quantity = sum(quantity)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        request.session['user_id'] = user.id
        request.session['%s_cart' % user.id] = quantity
        return JsonResponse({"errcode": "0", "errmsg": "login success"})


class LogoutView(View):
    """用户退出登录"""
    @method_decorator(user_auth)
    def get(self, request, user):
        del request.session['user_id']
        del request.session['%s_cart' % user.id]
        return JsonResponse(
            {"errcode": "0", "errmsg": "logout success", "data": {"url": settings.URL_PREFIX + '/index'}})


class UserView(View):

    @method_decorator(user_auth)
    def get(self, request, user):
        """获取用户信息"""
        # category = []
        # try:
        #     cates = Category.objects.filter(super_category__isnull=True)
        # except Exception as e:
        #     online_logger.error(e)
        #     return JsonResponse({"errcode": "102", "errmsg": "db error"})
        # for cate in cates:
        #     try:
        #         sub_cates = Category.objects.filter(super_category__id=cate.id)
        #     except Exception as e:
        #         online_logger.error(e)
        #         return JsonResponse({"errcode": "102", "errmsg": "db error"})
        #     category.append({"id": cate.id, "name": cate.name,
        #                      "sub_cates": [{'id': sub_cate.id, 'name': sub_cate.name} for sub_cate in sub_cates if
        #                                    sub_cates] if sub_cates else []})
        # context = {"category":category,"user": user}
        context = {"user": user}
        try:
            orders = Order.objects.filter(user=user)
            order_quantity = len(orders)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        cart_quantity = request.session.get("%s_cart" % user.id, 0)
        context.update({"order_quantity": order_quantity, "cart_quantity": cart_quantity})
        return render(request, "myAccount.html", context=context)

    @method_decorator(user_auth)
    def post(self, request, user):
        """修改用户信息"""
        username = request.POST.get("username", '')
        email = request.POST.get("email", None)
        if email:
            if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.(com|cn|net){1,3}$', email):
                return JsonResponse({"errcode": "106", "errmsg": "email format error"})
        phone = request.POST.get("phone", None)
        password = request.POST.get("password", None)
        repassword = request.POST.get("repassword", None)
        if password != repassword:
            return JsonResponse({"errcode": "106", "errmsg": "password differently"})
        if not all([username, email, phone, password, repassword]):
            return JsonResponse({"errcode": "101", "errmsg": "params not all"})
        password = make_password(password)
        try:
            user.username = username
            user.email = email
            user.password = password
            user.phone = phone
            user.save()
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        return JsonResponse({"errcode": "0", "result": "save success"})


class MyAddressView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        """获取用户地址"""
        context = {"user": user}
        useraddress = list(
            user.address.all().values('name', 'province', 'city', 'district', 'road', 'phone_number', 'postcode'))
        if useraddress:
            context.update({"useraddress": useraddress[0]})
        try:
            orders = Order.objects.filter(user=user)
            order_quantity = len(orders)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        cart_quantity = request.session.get("%s_cart" % user.id, 0)
        context.update({"order_quantity": order_quantity, "cart_quantity": cart_quantity})
        return render(request, "myAddress.html", context=context)

    @method_decorator(user_auth)
    def post(self, request, user):
        """修改用户地址"""
        name = request.POST.get("name", None)
        road = request.POST.get("road", None)
        district = request.POST.get("district", None)
        city = request.POST.get("city", None)
        province = request.POST.get("province", None)
        postcode = request.POST.get("postcode")
        phone_number = request.POST.get("phone_number", None)
        if not (name or road or district or city or province or phone_number or postcode):
            try:
                user.address.delete()
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            return JsonResponse({"errcode": "0", "errmsg": "save success"})
        else:
            useraddress = user.address.all()
            try:
                if len(useraddress) > 0:
                    useraddress = useraddress[0]
                    useraddress.name = name
                    useraddress.province = province
                    useraddress.city = city
                    useraddress.district = district
                    useraddress.road = road
                    useraddress.phone = phone_number
                    useraddress.save()
                else:
                    UserAddress.objects.create(name=name, province=province, city=city, district=district, road=road,
                                               phone_number=phone_number, postcode=postcode, user=user)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            return JsonResponse({"errcode": "0", "errmsg": "save success"})


class SignUpView(View):
    """注册"""
    def post(self, request):
        username = request.POST.get("username", None)
        email = request.POST.get("email", None)
        if email:
            if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.(com|cn|net){1,3}$', email):
                return JsonResponse({"errcode": "106", "errmsg": "email format error"})
        phone = request.POST.get("phone", None)
        if phone:
            if not re.match(r'^1[0-9]{10}$', phone):
                return JsonResponse({"errcode": "103", "errmsg": "phone format error"})
        try:
            users = User.objects.filter(Q(email=email) | Q(phone=phone))
            if len(users) > 0:
                return JsonResponse({"errcode": "109", "errmsg": "user has registered"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        password = request.POST.get("password", None)
        repassword = request.POST.get("repassword", None)
        if password != repassword:
            return JsonResponse({"errcode": "107", "errmsg": "password differently"})
        if not all([email, phone, password, repassword]):
            return JsonResponse({"errcode": "101", "errmsg": "params not all"})
        password = make_password(password)
        try:
            signup_date = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
            user = User.objects.create(email=email, phone=phone, password=password, signup_date=signup_date)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        request.session['user_id'] = user.id
        request.session['%s_cart' % user.id] = 0
        return JsonResponse(
            {"errcode": "0", "errmsg": "sign up success", "data": {"url": settings.URL_PREFIX + '/index'}})


class SignUpTemplateView(View):

    def get(self, request):
        category = []
        try:
            cates = Category.objects.filter(super_category__isnull=True)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        for cate in cates:
            try:
                sub_cates = Category.objects.filter(super_category__id=cate.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            category.append({"id": cate.id, "name": cate.name,
                             "sub_cates": [{'id': sub_cate.id, 'name': sub_cate.name} for sub_cate in sub_cates if
                                           sub_cates] if sub_cates else []})
        context = {"category": category, "user": ""}
        # context = {"user":""}
        return render(request, 'register.html', context=context)
