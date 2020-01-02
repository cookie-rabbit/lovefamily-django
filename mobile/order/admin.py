from django.contrib import admin

# Register your models here.

# @user_auth
# def order_detail(user_id, user, order_id):
#     if user_id == user.id:
#         try:
#             goods = Order_Goods.objects.filter(order_id=order_id)
#         except Exception as e:
#             online_logger.error(e)
#             return JsonResponse({"res": 111, "errmsg": "数据库错误"})
#         if goods != '':
#             good_dict = []
#             for good in goods:
#                 good_id = good.goods_id
#                 quantity = good.quantity
#                 good_detail = Goods.objects.get(id=good_id)
#                 good_name_en = good_detail.name_en
#                 good_price = good_detail.price
#                 good_description_en = good_detail.description_en
#                 good_image = str(good_detail.image)
#                 good_dict.append({"quantity": quantity, "good_name_en": good_name_en, "good_price": good_price,
#                                  "good_description_en": good_description_en, "good_image": good_image})
#             res = good_dict
#             JsonResponse({'errcode': 0, 'data': res})
#         JsonResponse({'errcode': 0, 'data': ''})