$(".contentContainer")
	/* 切换hot/new */
	.on("click", ".type li", function() {
		$(".type li").removeClass("current");
		$(this).addClass("current");
		var type = $(".type .current").data("type");
		var req = {
			url: baseUrl + 'goods/' + type + "/",
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".goods").remove();
					$(".content").html(res.data.result);
					if (res.data.more == true) {
						$(".content").append('<div class="more">MORE</div>');
					}
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
	.on("click", ".more", function() {
		var type = $(".type .current").data("type");
		var req = {
			url: baseUrl + 'goods/' + type + "/",
			data: {
				current: $(".content .goods").length
			},
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".more").before(res.data.result);
					if (res.data.more == false) {
						$(".more").remove();
					}
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
	.on("click", ".toCart", function() {
		var req = {
			url: baseUrl + 'carts/',
			data: {
				goods_id: $(this).data("id"),
				quantity: 1
			},
			method: "post",
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".toShoppingCart span").html(res.data.quantity);
					getToast01("Successfully joined the shopping cart");
				} else {
					getToast01(res.errmsg);
				}
			},
			errFun: function(err) {
				getToast01("Network anomaly!");
			}
		};
		doAjax(req);
		return false;
	})
	.on("click", ".toBuy", function() {
		var req = {
			url: baseUrl + 'carts/confirm/',
			method: "post",

			data: {
				goods_id: $(this).data("id"),
				goods_num: 1
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

		return false;
	})
	/* 列多分类数据 */
	.on("click", ".moreKinds", function() {
		var categoryId = $(".moreKinds").data("categoryid");
		var req = {
			url: baseUrl + 'goods/category/' + categoryId + "/",
			data: {
				current: $(".content .goods").length
			},
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".moreKinds").before(res.data.result);
					if (res.data.more == false) {
						$(".moreKinds").remove();
					}
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
	/* 更多搜索数据 */
	.on("click", ".moreResult", function() {
		var keyword = $(".moreResult").data("keyword");
		var req = {
			url: baseUrl + 'goods/search',
			data: {
				current: $(".content .goods").length,
				keyword: keyword
			},
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".moreResult").before(res.data.result);
					if (res.data.more == false) {
						$(".moreResult").remove();
					}
				} else {
					getToast01(res.errmsg);
				}
			},
			errFun: function(err) {
				getToast01("Network anomaly!");
			}
		};
		doAjax(req);
	});

$(document).ready(function() {
	var p = 0,
		t = 0;
	$(window).scroll(function(e) {
		p = $(this).scrollTop();
		if (t < p) {
			$(".footer").css("display", "block")
		} else if (t > p) {
			$(".footer").css("display", "none")
		}
		t = p;;
	});

});
