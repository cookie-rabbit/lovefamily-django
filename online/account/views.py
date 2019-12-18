import json
import re

from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from management.user.models import User, UserAddress
from online.goods.models import Category
from online.logger import online_logger
from utils.decorator import user_auth


class LoginView(View):

    def post(self,request):
        username = request.POST.get("name",None)
        password = request.POST.get("password",None)
        if not all([username,password]):
            return JsonResponse({"errcode":"101","errmsg":"params not all"})
        try:
            user = User.objects.filter(Q(email = username) | Q(username = username))
            if user is None:
                return JsonResponse({"errcode":"105","errmsg":"'please login after sign up"})
            user = user[0]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        if not user.check_password(password):
            return JsonResponse({"errcode":"104","errmsg":"password error"})
        request.session['user_id'] = user.id
        return JsonResponse({"errcode":"0","result":"login success"})


class LogoutView(View):

    @method_decorator(user_auth)
    def get(self,request,user):
        del request.session['user_id']
        return JsonResponse({"errcode":"0","errmsg":"logout success"})


class UserView(View):

    @method_decorator(user_auth)
    def get(self,request,user):
        context = {"email": user.email, "phone": user.phone, "password": user.password}
        useraddress = list(user.address.all().values('name','province','city','district','road','phone_number','postcode'))
        if useraddress:
            context.update(useraddress[0])
        print(timezone.now())
        return JsonResponse(context,safe=False)
        # return render(request,"my_account.html",context=context)


    @method_decorator(user_auth)
    def put(self,request,user):
        data = json.loads(request.body.decode())
        email = data.get("email", None)
        if email:
            if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.(com|cn|net){1,3}$', email):
                return JsonResponse({"errcode": "105", "errmsg": "email format error"})
        phone = data.get("phone", None)
        password = data.get("password", None)
        repassword = data.get("repassword", None)
        if password != repassword:
            return JsonResponse({"errcode": "106", "errmsg": "password differently"})
        if not all([email, phone, password, repassword]):
            return JsonResponse({"errcode": "101", "errmsg": "params not all"})
        password = make_password(password)
        try:
            user.email = email
            user.password = password
            user.phone = phone
            user.save()
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        name = data.get("name", None)
        road = data.get("road", None)
        district = data.get("district", None)
        city = data.get("city", None)
        province = data.get("province", None)
        postcode = data.get("postcode")
        phone_number = data.get("phone_number", None)
        if all([name, road, district, city, province, postcode, phone]) is None:
            try:
                user.address.delete()
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode":"102","errmsg":"db error"})
            return JsonResponse({"errcode": "0", "result": "save success"})
        else:
            useraddresss = user.address.all()[0]
            try:
                useraddresss.name = name
                useraddresss.province = province
                useraddresss.city = city
                useraddresss.district = district
                useraddresss.road = road
                useraddresss.phone = phone_number
                useraddresss.save()
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode":"102","errmsg":"db error"})
            return JsonResponse({"errcode": "0", "result": "save success"})


class SignUpView(View):
    def post(self,request):
        data = json.loads(request.body.decode())
        email = data.get("email",None)
        if email:
            if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.(com|cn|net){1,3}$',email):
                return JsonResponse({"errcode":"105","errmsg":"email format error"})
        phone = data.get("phone",None)
        password = data.get("password",None)
        repassword = data.get("repassword",None)
        if password != repassword:
            return JsonResponse({"errcode":"106","errmsg":"password differently"})
        if not all([email,phone,password,repassword]):
            return JsonResponse({"errcode":"101","errmsg":"params not all"})
        password = make_password(password)
        try:
            user = User.objects.create(email=email,phone=phone,password=password)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        name = data.get("name", None)
        road = data.get("road",None)
        district = data.get("district",None)
        city = data.get("city",None)
        province = data.get("province",None)
        postcode = data.get("postcode",None)
        phone_number = data.get("phone_number",None)
        if all([name,road,district,city,province,postcode,phone]) is None:
            request.session['user_id'] = user.id
            return JsonResponse({"errcode":"0","result":"sign up success"})
        else:
            try:
                useraddress = UserAddress(name=name,province=province,city=city,district=district,road=road,phone_number=phone_number,postcode=postcode,user=user)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode":"102","errmsg":"db error"})
            request.session['user_id'] = user.id
            return JsonResponse({"errcode":"0","result":"sign up success"})


class SignUpTemplateView(View):

    def get(self,request):
        return render(request,'register.html')


