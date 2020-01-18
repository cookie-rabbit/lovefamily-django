var deleteObj = undefined;
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
		count > 0 && editCart(me.parents(".cartGoods").data("id"), count);
		
	})
	.on("click", ".remove", function() {
		deleteObj = $(this);
		$(".content").after(getConfimDiv("Are you sure to delete?"));
	})
	.on("click", ".fixedDiv .confirm", function() {
		deleteObj.parents(".cartGoods").remove();
		setTotalCount();
		var req = {
			url: baseUrl + 'cart/' + deleteObj.parents(".cartGoods").data("id") + "/",
			method: "delete",
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".fixedDiv").remove();
					$(".toShoppingCart span").html(res.data.quantity);
				} else {
					getToast01(res.errmsg);
				}
			},
			errFun: function(err) {
				getToast01("Network anomaly!");
			}
		};
		doAjax(req);
	}).on("click", ".goBuy", function() {
		var params = "";
		for (var i = 0; i < $(".toBuyIt").length; i++) {
			params = params + $($(".toBuyIt")[i]).data("id") + ","
		}
		params = params.substr(0, params.length - 1)

		var req = {
			url: baseUrl + 'carts/confirm/',
			method: "post",
			data: {
				carts_id: params
			},
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					location.href = res.data.href;
				} else {
					getToast01(res.errmsg);
				}
			},
			errFun: function(err) {
				getToast01("Network anomaly!");
			}
		};
		doAjax(req);
	})


function editCart(cart_id, quantity) {
	var req = {
		url: baseUrl + 'cart/' + cart_id + "/",
		data: {
			quantity: quantity
		},
		method: "post",
		sucFun: function(res) {
			if (parseInt(res.errcode) === 0) {
				$(".toShoppingCart span").html(res.data.quantity);
			} else {
				getToast01(res.errmsg);
			}
		},
		errFun: function(err) {
			getToast01("Network anomaly!");
		}
	};
	doAjax(req);
}
