from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from management.user.models import User, Admin
from online.logger import online_logger

method_decorator(csrf_exempt)


def user_auth(func):
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get("user_id", None)
        if not user_id:
            return JsonResponse({"errcode": "105",
                                 "errmsg": "Please login love-family Online Shop! "
                                           "If you are not a member, please sign-up first! "})
        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "105",
                                 "errmsg": "Please login love-family Online Shop! "
                                           "If you are not a member, please sign-up first! "})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        return func(request, user, *args, **kwargs)

    return wrapper


def admin_auth(func):
    def wrapper(request, *args, **kwargs):
        # user_id = 1
        user_id = request.session.get("admin_id", None)
        if not user_id:
            return JsonResponse({"errcode": "105", "errmsg": "please login"})
        try:
            user = Admin.objects.get(id=user_id)
        except User.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find user in db"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "Db error"})
        return func(request, user, *args, **kwargs)

    return wrapper
