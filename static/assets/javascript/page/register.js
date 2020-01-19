$(".registerContainer")
	.on("click", ".toSubmit", function() {
		$(".baseInfor .tips").html("");	
		var name = $(".baseInfor .name input").val().trim();
		var email = $(".baseInfor .email input").val().trim();
		var phone = $(".baseInfor .phone input").val().trim();
		var password = $(".baseInfor .pass input").val().trim();
		var repassword = $(".baseInfor .repass input").val().trim();
		if (name.length == 0) {
			$(".baseInfor .name .tips").html("Please enter the username");
		}  else if (phone.length == 0) {
			$(".baseInfor .phone .tips").html("Please enter phone number");
		} else if (password.length == 0) {
			$(".baseInfor .pass .tips").html("Please input a password");
		} else if (password != repassword) {
			$(".baseInfor .repass .tips").html("Passwords must match");
		}
		 else {
			var req = {
				url: baseUrl + 'account/signup/',
				method: "post",
				data: {
					username:name,
					email: email,
					phone: phone,
					password: password,
					repassword: repassword
				},
				sucFun: function(res) {
					if (parseInt(res.errcode) === 0) {
						$(".myAccountContainer input").css("opcity", "0.7").attr("readonly", "true");
						$(".toSubmit").html("Edit").removeClass("toSave");
						getToast01(
							"Congraduations for becoming a member of Love Family.<br>Enjoy your purchasing trip!<br> Auto jump... ",
							2500);
						location.href = res.data.url;
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
