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
		$(".toContinue .continue").addClass("goBuy");

		$(".editAddress").addClass("hidden");
		$(".readAddress").removeClass("hidden");

		$(".readAddress .fullName").html($(".editAddress .fullName input").val());
		$(".readAddress .addressLine1").html($(".editAddress .addressLine1 input").val());
		$(".readAddress .addressLine2").html($(".editAddress .addressLine2 input").val());
		$(".readAddress .city").html($(".editAddress .city input").val());
		$(".readAddress .province").html($(".editAddress .province input").val());
		$(".readAddress .zip").html($(".editAddress .zip input").val());
		$(".readAddress .phoneNum span").html($(".editAddress .phoneNum input").val());
	});
$(".toContinue").on("click", ".goBuy", function() {

	var addressObj = {
		fullName: $(".readAddress .fullName").html(),
		addressLine1: $(".readAddress .addressLine1").html(),
		addressLine2: $(".readAddress .addressLine2").html(),
		city: $(".readAddress .city").html(),
		province: $(".readAddress .province").html(),
		zip: $(".readAddress .zip").html(),
		phoneNum: $(".readAddress .phoneNum span").html()
	}
	var arrs = [];
	for (var i = 0; i < $(".orderLines .cartGoods").length; i++) {
		var obj = {};
		var me = $(".orderLines .cartGoods")[i];
		obj.id = $(me).data("id");
		
		arrs[i] = obj;
	}
	/* todo:ajax请求 */
});
