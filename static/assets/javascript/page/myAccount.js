$(".myAccountContainer")
	.on("click", ".toSubmit", function() {
		$(".myAccountContainer input").removeAttr("readonly").css("opcity", "1.0");
		$(".myAccountContainer .user input").attr("readonly","readonly").css("opcity", "0.8");
		$(this).html("Save").addClass("toSave");
	})
	.on("click", ".toSave", function() {
		var email = $(".baseInfor .email input").val().trim();
		var phone = $(".baseInfor .phone input").val().trim();
		var password = $(".baseInfor .pass input").val().trim();
		var repassword = $(".baseInfor .repass input").val().trim();
		var strRegex = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
		$(".baseInfor .tips").html("");
		if (email.length == 0) {
			$(".baseInfor .email .tips").html("Please enter email");
		} else if (!strRegex.test(email)) {
			$(".baseInfor .email .tips").html("Please enter the correct email");
		} else if (phone.length == 0) {
			$(".baseInfor .phone .tips").html("Please enter phone number");
		} else if (password.length == 0) {
			$(".baseInfor .pass .tips").html("Please input a password");
		} else if (password != repassword) {
			$(".baseInfor .repass .tips").html("Passwords must match");
		} else {
			var req = {
				url: baseUrl + 'account/',
				method: "post",
				data: {
					email: email,
					phone: phone,
					password: password,
					repassword: repassword,
				},
				sucFun: function(res) {
					if (parseInt(res.errcode) === 0) {
						$(".myAccountContainer input").css("opcity", "0.7").attr("readonly", "true");
						$(".toSubmit").html("Edit").removeClass("toSave");
						getToast01(res.errmsg);
					}
				},
				errFun: function(err) {
					getToast01("Network anomaly!");
				}
			};
			doAjax(req);
		}


	});
