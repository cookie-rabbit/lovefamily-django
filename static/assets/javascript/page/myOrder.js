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
		var name = $(".editAddress .fullName input").val().trim();
		var addressLine1 = $(".editAddress .addressLine1 input").val();
		var addressLine2 = $(".editAddress .addressLine2 input").val().trim();
		var city = $(".editAddress .city input").val().trim();
		var province = $(".editAddress .province input").val().trim();
		var zip = $(".editAddress .zip input").val().trim();
		var phoneNum = $(".editAddress .phoneNum input").val().trim();
		if (name.length == 0 || addressLine1.length == 0 || addressLine2.length == 0 || city.length == 0 || province.length ==
			0 || zip.length == 0 || phoneNum.length == 0) {
			getToast01("Please enter the complete receiving information!");

		} else {
			$(".readAddress .fullName").html(name);
			$(".readAddress .addressLine1").html(addressLine1);
			$(".readAddress .addressLine2").html(addressLine2);
			$(".readAddress .city").html(city);
			$(".readAddress .province").html(province);
			$(".readAddress .zip").html(zip);
			$(".readAddress .phoneNum span").html(phoneNum);
			$(".toContinue .continue").addClass("goBuy");
			$(".editAddress").addClass("hidden");
			$(".readAddress").removeClass("hidden");
		}

	});
$(".toContinue").on("click", ".goBuy", function() {
	$(".myOrderContainer").after(getConfimDiv("Are you sure to make the order? "));
});
$(".container")
	.on("click", ".fixedDiv .confirm", function() {
		var addressObj = {
			name: $(".readAddress .fullName").html(),
			road: $(".readAddress .addressLine1").html(),
			district: $(".readAddress .addressLine2").html(),
			city: $(".readAddress .city").html(),
			province: $(".readAddress .province").html(),
			zip: $(".readAddress .zip").html(),
			phone: $(".readAddress .phoneNum span").html()
		}
		var arrs = [];
		for (var i = 0; i < $(".orderLines .cartGoods").length; i++) {
			var obj = {};
			var me = $(".orderLines .cartGoods")[i];
			obj.id = $(me).data("id");
			obj.good_count = $(me).data("count");
			arrs[i] = obj;
		}
		var req = {
			url: baseUrl + 'orders/',
			data: {
				addressObj: addressObj,
				goods: arrs,
			},
			method: "post",
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					location.href = res.data.href;
				}
				else{
					getToast01(res.data.errmsg);
				}
			},
			errFun: function(err) {
				getToast01("Network anomaly!!!");
			}
		};
		doAjax(req);
	});
