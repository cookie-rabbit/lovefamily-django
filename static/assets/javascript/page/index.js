$(".contentContainer")
	.on("click", ".type li", function() {
		$(".type li").removeClass("current");
		$(this).addClass("current");
		var type = $(".type .current").data("type");
		var req = {
			url: baseUrl + 'goods/' + type + "/",
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".goods").remove();
					$(".more").before(res.data);
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
	.on("click", ".more", function() {
		var type = $(".type .current").data("type");
		var req = {
			url: baseUrl + 'goods/' + type + "/",
			data: {
				current: $(".content .goods").length
			},
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".more").before(res.data);
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
				getToast01("Network anomaly!!!");
			}
		};
		doAjax(req);
		return false;
	})
	.on("click", ".toBuy", function() {
		location.href = $(this).data("href");
		return false;
	})
	/* 列多分类数据 */
	.on("click", ".moreKinds", function() {
		var categoryId = $(".moreKinds").data("categoryid");
		var req = {
			url: baseUrl + 'good/category/' + categoryId + "/",
			data: {
				current: $(".content .goods").length
			},
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					$(".more").before(res.data);
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
					$(".more").before(res.data);
				} else {
					getToast01(res.errmsg);
				}
			},
			errFun: function(err) {
				getToast01("Network anomaly!!!");
			}
		};
		doAjax(req);
	});
