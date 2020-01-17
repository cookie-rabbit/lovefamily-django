import re
import json
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


class LoginView(View):
    """用户登录，注册"""

    def post(self, request):
        data = json.loads(request.body.decode())
        type = data.get("type")
        if type == 'login':
            username = data.get("username")
            password = data.get("password")
            if not all([username, password]):
                return JsonResponse({"errcode": "101", "errmsg": "params not all"})
            try:
                user = User.objects.filter(Q(email=username) | Q(phone=username))
                if user:
                    user = user[0]
                else:
                    return JsonResponse({"errcode": "105", "errmsg": "The user has not registered yet"})
                if user.status != 1:
                    return JsonResponse({"errcode": "116", "errmsg": "The user has been forbidden"})
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            if not user.check_password(password):
                return JsonResponse({"errcode": "104", "errmsg": "Password error"})
            try:
                carts = Cart.objects.filter(user__id=user.id)
                quantity = [cart.quantity for cart in carts]
                quantity = sum(quantity)
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            request.session['user_id'] = user.id
            request.session['%s_cart' % user.id] = quantity
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip_address = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip_address = request.META['REMOTE_ADDR']
            text = "The user who's user_id {} has been logged in at {},the ip address is {}".format(user.id,
                                                                                                    timezone.now(),
                                                                                                    ip_address)
            mobile_logger.info(text)
            return JsonResponse({"errcode": "0", "errmsg": "login success"})

        elif type == 'signup':
            data = json.loads(request.body.decode())
            username = data.get("username", None)
            if len(username) > 20:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for username"})
            email = data.get("email", None)
            if email:
                if not re.match(r'^([A-Za-z0-9_\-.])+@([A-Za-z0-9_\-.])+\.([A-Za-z]{2,7})$', email):
                    return JsonResponse({"errcode": "106", "errmsg": "email format error"})
            phone = data.get("phone", None)
            if len(phone) > 40:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for phone"})
            # if phone:
            #     if not re.match(
            #             r'^(((\\+\\d{2}-)?0\\d{2,3}-\\d{7,8})|((\\+\\d{2}-)?(\\d{2,3}-)?([1][3,4,5,7,8][0-9]\\d{8})))$',
            #             phone):
            #         return JsonResponse({"errcode": "106", "errmsg": "phone format error"})
            try:
                users = User.objects.filter(Q(email=email) | Q(phone=phone) | Q(username=username))
                if len(users) > 0:
                    return JsonResponse({"errcode": "109", "errmsg": "user has been registered"})
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            password = data.get("password", None)
            if len(password) > 100:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for password"})
            if password:
                if not re.match(r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,50}$', password):
                    return JsonResponse(
                        {"errcode": "106",
                         "errmsg": "The password must have both number and letters, not allowed the others."
                                   " The length of password must longer than six "})
            repassword = data.get("re_password", None)
            if password != repassword:
                return JsonResponse({"errcode": "107", "errmsg": "Passwords must be matched"})
            if not all([email, phone, password, repassword]):
                return JsonResponse({"errcode": "101", "errmsg": "params not all"})
            password = make_password(password)
            try:
                signup_date = timezone.localtime(timezone.now()).strftime("%Y-%m-%d")
                user = User.objects.create(username=username, email=email, phone=phone, password=password,
                                           signup_date=signup_date)
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            return JsonResponse(
                {"errcode": "0", "errmsg": "sign up success"})


class LogoutView(View):
    """用户退出登录"""

    @method_decorator(user_auth)
    def get(self, request, user):
        del request.session['user_id']
        del request.session['%s_cart' % user.id]
        return JsonResponse(
            {"errcode": "0", "errmsg": "logout success"})


class UserView(View):

    @method_decorator(user_auth)
    def get(self, request, user):
        type = request.GET.get("type", None)
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
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            # cart_quantity = request.session.get("%s_cart" % user.id, 0)
            # context.update({"order_quantity": order_quantity, "cart_quantity": cart_quantity})
            return JsonResponse({"errcode": "0", "data": data})
        elif type == "address":
            """获取用户地址"""
            try:
                user = User.objects.get(id=user.id)
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            useradd = UserAddress.objects.filter(user_id=user.id)
            if useradd:
                useradd = useradd[0]
                name = useradd.name
                province = useradd.province
                city = useradd.city
                district = useradd.district
                road = useradd.road
                phone_number = useradd.phone_number
                postcode = useradd.postcode
                data = {"name": name, "province": province, "city": city, "district": district,
                        "road": road, "phone_number": phone_number, "postcode": postcode}
            else:
                data = {"name": '', "province": '', "city": '', "district": '',
                        "road": '', "phone_number": '', "postcode": ''}

            return JsonResponse({"errcode": "0", "data": data})

    @method_decorator(user_auth)
    def post(self, request, user):
        data = json.loads(request.body.decode())
        type = data.get('type', None)
        if type == "info":
            """修改用户信息"""
            email = data.get("email", None)
            if email:
                if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.(com|cn|net){1,3}$', email):
                    return JsonResponse({"errcode": "106", "errmsg": "email format error"})
            phone = data.get("phone", None)
            if len(phone) > 15:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for road"})
            # if phone:
            #     if not re.match(
            #             r'^(((\\+\\d{2}-)?0\\d{2,3}-\\d{7,8})|((\\+\\d{2}-)?(\\d{2,3}-)?([1][3,4,5,7,8][0-9]\\d{8})))$',
            #             phone):
            #         return JsonResponse({"errcode": "106", "errmsg": "phone format error"})
            password = data.get("password", None)
            re_password = data.get("re_password", None)
            if password != re_password:
                return JsonResponse({"errcode": "106", "errmsg": "password differently"})
            if not all([email, phone, password, re_password]):
                return JsonResponse({"errcode": "101", "errmsg": "params not all"})
            password = make_password(password)

            judge_phone = User.objects.filter(phone=phone).exclude(id=user.id)
            if len(judge_phone) > 0:
                return JsonResponse({"errcode": "115", "errmsg": "phone number has been exist"})
            judge_email = User.objects.filter(phone=email).exclude(id=user.id)
            if len(judge_email) > 0:
                return JsonResponse({"errcode": "115", "errmsg": "email number has been exist"})
            try:
                user.email = email
                user.password = password
                user.phone = phone
                user.save()
            except Exception as e:
                mobile_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "Db error"})
            return JsonResponse({"errcode": "0", "errmsg": "save success"})

        elif type == "address":
            """修改用户地址"""
            name = data.get("name", None)
            if len(name) > 40:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for name"})
            road = data.get("road", None)
            if len(road) > 100:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for road"})
            district = data.get("district", None)
            if len(district) > 100:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for district"})
            city = data.get("city", None)
            if len(city) > 100:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for city"})
            province = data.get("province", None)
            if len(province) > 100:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for province"})
            postcode = data.get("postcode", None)
            if len(postcode) > 40:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for postcode"})
            phone_number = data.get("phone_number", None)
            if len(phone_number) > 40:
                return JsonResponse({"errcode": "115", "errmsg": "the content is too long for phone_number"})
            if not (name or road or district or city or province or phone_number or postcode):
                try:
                    user.address.delete()
                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "Db error"})
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
                        useraddress.postcode = postcode
                        useraddress.phone_number = phone_number
                        useraddress.save()
                    else:
                        UserAddress.objects.create(name=name, province=province, city=city, district=district,
                                                   road=road,
                                                   phone_number=phone_number, postcode=postcode, user=user)
                except Exception as e:
                    mobile_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "Db error"})
                return JsonResponse({"errcode": "0", "errmsg": "save success"})
        else:
            return JsonResponse({"errcode": "101", "errmsg": "params 'type' can't find"})
