/* 初始默认全选择 */
$(function() {
	setTotalCount();
})
/* 设置总价格 */
function setTotalCount() {
	var totalSum = 0;
	for (var i = 0; i < $(".toBuyIt").length; i++) {
		var obj = $($(".toBuyIt")[i]);
		var price = parseFloat(obj.find(".price span").html());
		var count = parseFloat(obj.find(".count").val());
		totalSum += price * count;
	}
	totalSum === 0 ? $(".buyNow").removeClass("goBuy") : $(".buyNow").addClass("goBuy");
	$(".totalPrice span").html(totalSum);
}

$(".myCartContainer")
	.on("click", ".checkOrNot", function() {
		var me = $(this);
		me.toggleClass("checked");
		if (me.hasClass("checked")) {
			me.parents(".cartGoods").addClass("toBuyIt");
		} else {
			me.parents(".cartGoods").removeClass("toBuyIt");
		}
		setTotalCount();
	})
	.on("click", ".add", function() {
		var me = $(this);
		var count = me.parents(".quantity").find(".count").val();
		count = parseInt(count) + 1;
		me.parents(".quantity").find(".count").val(count);
		setTotalCount();
		editCart(me.parents(".cartGoods").data("id"), count);

	})
	.on("click", ".sub", function() {
		var me = $(this);
		var count = me.parents(".quantity").find(".count").val();
		if (count > 1) {
			count = parseInt(count) - 1;
			me.parents(".quantity").find(".count").val(count);
		}
		setTotalCount();
		editCart(me.parents(".cartGoods").data("id"), count);
	})
	.on("click", ".remove", function() {
		var me = $(this);
		me.parents(".cartGoods").remove();
		setTotalCount();
		var req = {
			url: baseUrl + 'carts/' + me.parents(".cartGoods").data("id") + "/",
			method: "delete",
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".toShoppingCart span").html(res.data.quantity);
				} else {
					getToast01(res.errmsg);
				}
			},
			errFun: function(err) {
				getToast01("Network anomaly!!!");
			}
		};
		doAjax(req);
	})


function editCart(cart_id, quantity) {
	var req = {
		url: baseUrl + 'carts/' + cart_id + "/",
		data: {
			quantity: quantity
		},
		method: "put",
		sucFun: function(res) {
			if (parseInt(res.errcode) === 0) {
				$(".toShoppingCart span").html(res.data.quantity);
			} else {
				getToast01(res.errmsg);
			}
		},
		errFun: function(err) {
			getToast01("Network anomaly!!!");
		}
	};
	doAjax(req);
}
