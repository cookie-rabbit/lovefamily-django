import json
import re

from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render



# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from management.constants import PER_PAGE_USER_COUNT
from management.user.models import User
from management.logger import management_logger
from utils.decorator import admin_auth


class LoginView(View):

    def post(self,request):
        """管理员登录"""
        data = json.loads(request.body.decode())
        username = data.get("username",None)
        password = data.get("password",None)
        if not all([username,password]):
            return JsonResponse({"errcode":"101","errmsg":'params not all'})
        try:
            user = User.objects.filter(username=username)
            if not user:
                return JsonResponse({"errcode":"102","errmsg":"can not find user in db"})
            else:
                user = user[0]
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        if not user.is_admin:
            return JsonResponse({"errcode":"103","errmsg":"not permission to access"})
        if not user.check_password(password):
            return JsonResponse({"errcode":"104","errmsg":"password error"})
        request.session['user_id'] = user.id
        return JsonResponse({"errcode":"0","errmsg":"login success"})


class UsersView(View):
    @method_decorator(admin_auth)
    def get(self,request,user):
        """获取用户列表"""
        username = request.GET.get("username",None)
        phone = request.GET.get("phone", None)
        email = request.GET.get("email", None)
        page = request.GET.get("page",1)
        try:
            page = int(page)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode":"101","errmsg":"params errror"})
        search_dict = {}
        if username:
            search_dict["username"] = username
        if phone:
            search_dict["phone"] = phone
        if email:
            search_dict['email'] = email
        try:
            users = User.objects.filter(**search_dict)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        paginator = Paginator(users, PER_PAGE_USER_COUNT)
        user_list = paginator.page(page)
        result = [{"id":user.id,"username":user.username,"phone":user.phone,"signup_date":user.signup_date,"status":user.status} for user in user_list]
        return JsonResponse({"errcode": "0", "data": result})


class UserView(View):
    @method_decorator(admin_auth)
    def get(self,request,user,user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            management_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"can not find user in db"})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        result = {"id":user.id,"email": user.email, "phone": user.phone, "password": user.password}
        useraddress = list(
            user.address.all().values('name', 'province', 'city', 'district', 'road', 'phone_number', 'postcode'))
        if useraddress:
            result.update(useraddress[0])
        return JsonResponse({"errcode":"0","data":result})

    @method_decorator(admin_auth)
    def put(self,request,user):
        data = json.loads(request.body.decode())
        # email = data.get("email", None)
        # if email:
        #     if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.(com|cn|net){1,3}$', email):
        #         return JsonResponse({"errcode": "105", "errmsg": "email format error"})
        # phone = data.get("phone", None)
        password = data.get("password", None)
        repassword = data.get("repassword", None)
        status = data.get('status',True)
        if password != repassword:
            return JsonResponse({"errcode": "106", "errmsg": "password differently"})
        if not all([password, repassword]):
            return JsonResponse({"errcode": "101", "errmsg": "params not all"})
        password = make_password(password)
        try:
            # user.email = email

            # user.phone = phone
            user.password = password
            user.status = status
            user.save()
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        name = data.get("name", None)
        road = data.get("road", None)
        district = data.get("district", None)
        city = data.get("city", None)
        province = data.get("province", None)
        postcode = data.get("postcode")
        phone_number = data.get("phone_number", None)
        if all([name, road, district, city, province, postcode, phone_number]) is None:
            try:
                user.address.delete()
            except Exception as e:
                management_logger.error(e)
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
                management_logger.error(e)
                return JsonResponse({"errcode":"102","errmsg":"db error"})
            return JsonResponse({"errcode": "0", "errmsg": "update success"})

