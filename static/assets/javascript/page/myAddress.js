$(".registerContainer")
	/* 当没有用户地址的时候 */
	.on("click", ".noAddress .toSubmit", function() {
		addressChange();
	})
	.on("click", ".toSave", function() {
		addressChange();
	})
	.on("click", ".haveAddress .toEdit", function() {
		$(".registerContainer input").removeAttr("readonly").css("opcity", "1.0");
		$(".addressContent").removeClass("haveAddress")
		$(this).html("Save").addClass("toSave");
	})

function addressChange() {
	var name = $(".addressContent .fullName input").val();
	var road = $(".addressContent .addressLine1 input").val();
	var district = $(".addressContent .addressLine2 input").val();
	var city = $(".addressContent .city input").val();
	var province = $(".addressContent .province input").val();
	var postcode = $(".addressContent .zip input").val();
	var phone_number = $(".addressContent .phoneNum input").val();
	if (name.length == 0 || district.length == 0 || city.length == 0 || city.length == 0 || province.length ==
		0 || postcode.length == 0 || phone_number.length == 0) {
		getToast01("Please enter the complete receiving information!");
	} else {
		var req = {
			url: baseUrl + 'address/',
			method: "post",
			data: {
				name: name,
				road: road,
				district: district,
				city: city,
				province: province,
				postcode: postcode,
				phone_number: phone_number
			},
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					location.reload();
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
}
