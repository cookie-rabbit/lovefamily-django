$(".registerContainer")
	.on("click", ".toSubmit", function() {
		var baseInfor = formatObjVal({
			name: $(".baseInfor .name input").val(),
			phone: $(".baseInfor .phone input").val(),
			pass: $(".baseInfor .pass input").val(),
			repass:$(".baseInfor .repass input").val()
		})

		if (setTips(baseInfor.name, baseInfor.pass, baseInfor.repass)) {
			var addressObj = formatObjVal({
				fullName: $(".addressContent .fullName input").val(),
				addressLine1: $(".addressContent .addressLine1 input").val(),
				addressLine2: $(".addressContent .addressLine2 input").val(),
				city: $(".addressContent .city input").val(),
				province: $(".addressContent .province input").val(),
				zip: $(".addressContent .zip input").val(),
				phoneNum: $(".addressContent .phoneNum input").val()
			});

		}
	})
	.on("input propertychange", function() {
		var nameL = $(".baseInfor .name input").val().trim().replace(/\s/g, "").length;
		var phoneL = $(".baseInfor .phone input").val().trim().replace(/\s/g, "").length;
		var passL = $(".baseInfor .pass input").val().trim().replace(/\s/g, "").length;
		var repassL = $(".baseInfor .repass input").val().trim().replace(/\s/g, "").length;
		console.log(nameL > 0 && phoneL > 0 && passL > 0 && repassL > 0);
		if (nameL > 0 && phoneL > 0 && passL > 0 && repassL > 0) {
			$(".submit").addClass("toSubmit");
		} else {
			$(".submit").removeClass("toSubmit");
		}
	});

function setTips(name, pass, repass) {
	var regEmail = /([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)/;
	if (regEmail.test(name) == false) {
		$(".baseInfor .name .tips").removeClass("hidden");
		return false;
	} else {
		$(".baseInfor .name .tips").addClass("hidden");
	}
	if (pass !== repass) {
		$(".baseInfor .repass .tips").removeClass("hidden");
		return false;
	} else {
		$(".baseInfor .repass .tips").addClass("hidden");
	}
	return true;
}
