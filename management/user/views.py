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

    def post(self, request):
        """管理员登录"""
        data = json.loads(request.body.decode())
        username = data.get("username", None)
        password = data.get("password", None)
        if not all([username, password]):
            return JsonResponse({"errcode": "101", "errmsg": 'params not all'})
        try:
            user = User.objects.filter(username=username)
            if not user:
                return JsonResponse({"errcode": "102", "errmsg": "can not find user in db"})
            else:
                user = user[0]
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        if not user.is_admin:
            return JsonResponse({"errcode": "103", "errmsg": "not permission to access"})
        if not user.check_password(password):
            return JsonResponse({"errcode": "104", "errmsg": "password error"})
        request.session['user_id'] = user.id
        return JsonResponse({"errcode": "0", "errmsg": "login success"})


class UsersView(View):
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取用户列表"""
        username = request.GET.get("username", None)
        phone = request.GET.get("phone", None)
        email = request.GET.get("email", None)
        page = request.GET.get("page", 1)
        try:
            page = int(page)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "params errror"})
        # search_dict = {}
        # if username:
        #     search_dict["username"] = username
        # if phone:
        #     search_dict["phone"] = phone
        # if email:
        #     search_dict['email'] = email
        try:
            if username and phone and email:
                users = User.objects.filter(email__contains=email).filter(phone__contains=phone).filter(
                    username__contains=username)
            elif username and phone:
                users = User.objects.filter(username__contains=username).filter(phone__contains=phone)
            elif username and email:
                users = User.objects.filter(username__contains=username).filter(email__contains=email)
            elif phone and email:
                users = User.objects.filter(phone__contains=phone).filter(email__contains=email)
            else:
                users = User.objects.all()
            total = len(users)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        paginator = Paginator(users, PER_PAGE_USER_COUNT)
        user_list = paginator.page(page)
        page_num = paginator.num_pages
        result = []
        for user in user_list:
            info = {"id": user.id, "username": user.username, "email": user.email, "phone": user.phone,
                    "signup_date": user.signup_date, "status": user.status, "password": 111111}
            useraddress = list(
                user.address.all().values('name', 'province', 'city', 'district', 'road', 'phone_number', 'postcode'))
            if useraddress:
                info.update(useraddress[0])
            result.append(info)
        return JsonResponse({"errcode": "0", "data": result, "page_num": page_num, "total": total})


class UserView(View):

    @method_decorator(admin_auth)
    def put(self, request, user, user_id):
        """修改用户密码和状态"""
        data = json.loads(request.body.decode())
        password = data.get("password", None)
        status = data.get('status', True)
        password = make_password(password)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find user in db"})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        try:
            if password:
                user.password = password
            if status:
                user.status = status
            user.save()
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        return JsonResponse({"errcode": "0", "errmsg": "update success"})
