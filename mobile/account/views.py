import re

from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from management.user.models import User, UserAddress
from mobile.logger import mobile_logger
from online.cart.models import Cart
from utils.decorator import user_auth
from weigan_shopping import settings


class LoginView(View):
    """用户登录，注册"""

    def post(self, request):
        type = request.POST.get('type', None)
        if type == 'login':
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
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            if not user.check_password(password):
                return JsonResponse({"errcode": "104", "errmsg": "password error"})
            try:
                carts = Cart.objects.filter(user__id=user.id)
                quantity = [cart.quantity for cart in carts]
                quantity = sum(quantity)
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            request.session['user_id'] = user.id
            request.session['%s_cart' % user.id] = quantity
            return JsonResponse({"errcode": "0", "errmsg": "login success"})

        elif type == 'signup':
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
                mobile_logger.error(e)
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
                user = User.objects.create(username=username, email=email, phone=phone, password=password, signup_date=signup_date)
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            request.session['user_id'] = user.id
            request.session['%s_cart' % user.id] = 0
            return JsonResponse(
                {"errcode": "0", "errmsg": "sign up success", "data": {"url": settings.URL_PREFIX + '/index'}})


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
        type = request.POST.get('type', None)
        if type == "info":
            """获取用户信息"""
            try:
                user = User.objects.get(id=user.id)
                id = user.id
                username = user.username
                email = user.email
                phone = user.phone
                password = 111111
                re_password = 111111
                data = {"id": id, "username": username, "email": email, "phone": phone, "password": password,
                        "re_password": re_password}
                # orders = Order.objects.filter(user=user)
                # order_quantity = len(orders)
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            # cart_quantity = request.session.get("%s_cart" % user.id, 0)
            # context.update({"order_quantity": order_quantity, "cart_quantity": cart_quantity})
            return JsonResponse({"errcode": "0", "data": data})
        elif type == "address":
            """获取用户地址"""
            try:
                user = User.objects.get(id=user.id)
                useradd = UserAddress.objects.get(user_id=user.id)
                name = useradd.name
                province = useradd.province
                city = useradd.city
                district = useradd.district
                road = useradd.road
                phone_number = useradd.phone_number
                postcode = useradd.postcode
                data = {"useradd": useradd, "name": name, "province": province, "city": city, "district": district,
                        "road": road, "phone_number": phone_number, "postcode": postcode}
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            return JsonResponse({"errcode": "0", "data": data})

    @method_decorator(user_auth)
    def post(self, request, user):
        type = request.POST.get('type', None)
        if type == "info":
            """修改用户信息"""
            email = request.POST.get("email", None)
            if email:
                if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.(com|cn|net){1,3}$', email):
                    return JsonResponse({"errcode": "106", "errmsg": "email format error"})
            phone_number = request.POST.get("phone_number", None)
            password = request.POST.get("password", None)
            re_password = request.POST.get("re_password", None)
            if password != re_password:
                return JsonResponse({"errcode": "106", "errmsg": "password differently"})
            if not all([email, phone_number, password, re_password]):
                return JsonResponse({"errcode": "101", "errmsg": "params not all"})
            password = make_password(password)

            judge_phone = User.objects.filter(phone=phone_number).exclude(id=user.id)
            if len(judge_phone) > 0:
                return JsonResponse({"errcode": "115", "errmsg": "phone number has been exist"})
            judge_email = User.objects.filter(phone=email).exclude(id=user.id)
            if len(judge_email) > 0:
                return JsonResponse({"errcode": "115", "errmsg": "email number has been exist"})

            try:
                user.email = email
                user.password = password
                user.phone = phone_number
                user.save()
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            return JsonResponse({"errcode": "0", "result": "save success"})

        elif type == "address":
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
                    mobile_logger.error(e)
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
                        UserAddress.objects.create(name=name, province=province, city=city, district=district,
                                                   road=road,
                                                   phone_number=phone_number, postcode=postcode, user=user)
                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "db error"})
                return JsonResponse({"errcode": "0", "errmsg": "save success"})
