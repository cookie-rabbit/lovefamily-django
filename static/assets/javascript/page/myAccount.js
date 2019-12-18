$(".myAccountContainer")
	.on("click", ".toSubmit", function() {
		$(".myAccountContainer input").removeAttr("readonly");
		$(this).removeClass("toSubmit").html("Save");
	})
	.on("input propertychange", function() {
		$(".submit").addClass("toSubmit").addClass("toSave");
	})
	.on("click", ".toSave", function() {
		var baseInfor = formatObjVal({
			name: $(".baseInfor .name").val(),
			phone: $(".baseInfor .phone").val(),
			pass: $(".baseInfor .pass").val(),
			repass: $(".baseInfor .repass").val()
		});
		var addressObj = formatObjVal({
			fullName: $(".addressContent .fullName input").val(),
			addressLine1: $(".addressContent .addressLine1 input").val(),
			addressLine2: $(".addressContent .addressLine2 input").val(),
			city: $(".addressContent .city input").val(),
			province: $(".addressContent .province input").val(),
			zip: $(".addressContent .zip input").val(),
			phoneNum: $(".addressContent .phoneNum input").val()
		});
	});
