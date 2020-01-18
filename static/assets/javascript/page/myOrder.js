$(".myOrderContainer")
	.on("click", ".edit", function() {
		$(".toContinue .continue").removeClass("goBuy");

		$(".readAddress").addClass("hidden");
		$(".editAddress").removeClass("hidden");

		$(".editAddress .fullName input").val($(".readAddress .fullName").html());
		$(".editAddress .addressLine1 input").val($(".readAddress .addressLine1").html());
		$(".editAddress .addressLine2 input").val($(".readAddress .addressLine2").html());
		$(".editAddress .city input").val($(".readAddress .city").html());
		$(".editAddress .province input").val($(".readAddress .province").html());
		$(".editAddress .zip input").val($(".readAddress .zip").html());
		$(".editAddress .phoneNum input").val($(".readAddress .phoneNum span").html());
	})
	.on("click", ".confirm", function() {
		var name = $(".editAddress .fullName input").val();
		var road = $(".editAddress .addressLine1 input").val();
		var district = $(".editAddress .addressLine2 input").val();
		var city = $(".editAddress .city input").val();
		var province = $(".editAddress .province input").val();
		var postcode = $(".editAddress .zip input").val();
		var phoneNum = $(".editAddress .phoneNum input").val();
		if (name.length == 0 || district.length == 0 || city.length == 0 || city.length == 0 || province.length ==
			0 || postcode.length == 0 || phoneNum.length == 0) {
			getToast01("Please enter the complete receiving information!");

		} else {
			var req = {
				url: baseUrl + 'orders/address',
				data: {
					name: name,
					province: province,
					city: city,
					district: district,
					road: road,
					postcode: postcode,
					phone_number: phoneNum
				},
				method: "post",
				sucFun: function(res) {
					if (parseInt(res.errcode) === 0) {
						$(".readAddress .fullName").html(name);
						$(".readAddress .addressLine1").html(road);
						$(".readAddress .addressLine2").html(district);
						$(".readAddress .city").html(city);
						$(".readAddress .province").html(province);
						$(".readAddress .zip").html(postcode);
						$(".readAddress .phoneNum span").html(phoneNum);
						$(".toContinue .continue").addClass("goBuy");
						$(".editAddress").addClass("hidden");
						$(".readAddress").removeClass("hidden");
					} else {
						getToast01(res.data.errmsg);
					}
				},
				errFun: function(err) {
					getToast01("Network anomaly!");
				}
			};
			doAjax(req);
		}

	});
$(".toContinue").on("click", ".goBuy", function() {
	$(".myOrderContainer").after(getConfimDiv("Are you sure to make the order? "));
});
$(".container")
	.on("click", ".fixedDiv .confirm", function() {
		var arrs = [];
		for (var i = 0; i < $(".orderLines .cartGoods").length; i++) {
			var obj = {};
			var me = $(".orderLines .cartGoods")[i];
			obj.good_id = $(me).data("id");
			obj.good_count = $(me).data("count");
			arrs[i] = obj;
		}
		console.log(JSON.stringify(arrs));
		var req = {
			url: baseUrl + 'orders/',
			data: {
				goods: JSON.stringify(arrs),
				/* tital:$(".totalPrice").data("price"), */
				is_cart:$(".myOrderContainer").data("cart")
			},
			method: "post",
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
	});
