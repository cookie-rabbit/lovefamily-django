$(".myOrdersContainer")
	.on("click", ".content .orderList h3", function() {
		var me=$(this);
		me.toggleClass("spread");
		var detailObj = $(this).parents(".orderList").find(".details");
		if (detailObj.length > 0) {
			detailObj.toggleClass("hidden");
		} else {
			/* ajax请求 */
			var req = {
				url: baseUrl + 'order/?order_no='+me.find(".order span").html(),
				sucFun: function(res) {
					if (parseInt(res.errcode) === 0) {
						me.after(res.data.result);
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
	})
	.on("click", ".more", function() {
		var req = {
			url: baseUrl + 'orders/more',
			data: {
				status: $(".myOrdersContainer .content .current").data("type"),
				offset: $(".orderList").length
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
	.on("click", ".searchPic", function() {

	});
