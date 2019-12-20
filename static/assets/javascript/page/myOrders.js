$(".myOrdersContainer")
	.on("click", ".content .orderList h3", function() {
		$(this).toggleClass("spread");
		var detailObj = $(this).parents(".orderList").find(".details");
		if(detailObj.length>0){
			detailObj.toggleClass("hidden");
		}
		else{
			/* ajax请求 */
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
		}
	})
	.on("click",".more",function(){
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
	})
	.on("click",".searchPic",function(){
		
	});
