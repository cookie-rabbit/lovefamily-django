import json

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render



# Create your views here.
from django.views import View
from management.user.models import User
from management.logger import management_logger


class LoginView(View):

    def post(self,request):
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
            return JsonResponse({"errcode":"104","errmsg":"pasword error"})
        request.session['user_id'] = user.id
        return JsonResponse({"errcode":"0","result":"ok"})


class UsersView(View):
    def get(self,request):
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
        try:
            users = User.objects.all()
            if username:
                users = users.objects.filter(username=username)
            if phone:
                users = users.objects.filter(mobile=phone)
            if email:
                users = users.objects.filter(email=email)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        paginator = Paginator(users, 10)
        user_list = paginator.page(page)

        return JsonResponse({"errcode": "0", "result": "ok"})
