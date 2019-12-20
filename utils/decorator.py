from django.http import JsonResponse

from management.user.models import User
from online.logger import online_logger


def user_auth(func):
    def wrapper(request, *args, **kwargs):
        # user_id = 1
        user_id = request.session.get("user_id", None)
        if not user_id:
            return JsonResponse({"errcode": "107", "errmsg": "please login"})
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find user in db"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        return func(request,user,*args, **kwargs)
    return wrapper


def admin_auth(func):
    def wrapper(request, *args, **kwargs):
        user_id = 1
        # user_id = request.session.get("user_id", None)
        if not user_id:
            return JsonResponse({"errcode": "107", "errmsg": "please login"})
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find user in db"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        if not user.is_admin:
            return JsonResponse({"errcode": "103", "errmsg": "no permission to access"})
        return func(request,user,*args, **kwargs)
    return wrapper