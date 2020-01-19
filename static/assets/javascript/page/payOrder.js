$(".payOrderContainer")
	.on("input propertychange", function() {
		var nameL = $(".cartContent .name input").val().trim().length;
		var cardL = $(".cartContent .card input").val().trim().length;
		if (nameL > 0 && cardL > 0) {
			$(".continue").addClass("toPay");
		} else {
			$(".continue").removeClass("toPay");
		}
	}).on("click", ".add", function() {
		var me = $(this);
		var count = me.parents(".dOrY").find(".count").val();
		count = parseInt(count) + 1;
		me.parents(".dOrY").find(".count").val(count)
	})
	.on("click", ".sub", function() {
		var me = $(this);
		var count = me.parents(".dOrY").find(".count").val();
		if (count > 1) {
			count = parseInt(count) - 1;
			me.parents(".dOrY").find(".count").val(count);
		}
	})
	.on("click", ".toPay", function() {
		var name = $(".cartContent .name input").val();
		var card = $(".cartContent .card input").val();
		var month = $(".day .count").val();
		var year = $(".year .count").val();
		var checked = $(".checkToAdd").hasClass("checked");
		var order_id = $(this).data("orderid");
		var req = {
			url: baseUrl + 'carts/'+order_id+'/pay',
			data: {
				name:name,
				card:card,
				month:month,
				year:year,
				checked:checked,
				order_id:order_id
			},
			method: "post",
			sucFun: function(res) {
				getToast01(res.errmsg);	
			},
			errFun: function(err) {
				getToast01("Network anomaly!");
			}
		};
		doAjax(req);

	})
	.on("click", ".checkToAdd", function() {
		$(".checkToAdd .check").toggleClass("checked");
	});
