/* 初始默认全选择 */
$(function() {
	setTotalCount();
})
/* 设置总价格 */
function setTotalCount() {
	var totalSum = 0;
	for (var i = 0; i < $(".toBuyIt").length; i++) {
		var obj = $($(".toBuyIt")[i]);
		var price = parseFloat(obj.find(".price span").html());
		var count = parseFloat(obj.find(".count").val());
		totalSum += price * count;
	}
	totalSum === 0 ? $(".buyNow").removeClass("goBuy") : $(".buyNow").addClass("goBuy");
	$(".totalPrice span").html(totalSum);
}

$(".contentContainer")
	.on("click", ".checkOrNot", function() {
		var me = $(this);
		me.toggleClass("checked");
		if (me.hasClass("checked")) {
			me.parents(".cartGoods").addClass("toBuyIt");
		} else {
			me.parents(".cartGoods").removeClass("toBuyIt");
		}
		setTotalCount();
	})
	.on("click", ".add", function() {
		var me = $(this);
		var count = me.parents(".quantity").find(".count").val();
		count = parseInt(count) + 1;
		me.parents(".quantity").find(".count").val(count)
		setTotalCount();
	})
	.on("click", ".sub", function() {
		var me = $(this);
		var count = me.parents(".quantity").find(".count").val();
		if (count > 1) {
			count = parseInt(count) - 1;
			me.parents(".quantity").find(".count").val(count);
		}
		setTotalCount();
	})
	.on("click", ".remove", function() {
		var me = $(this);
		me.parents(".cartGoods").remove();
		setTotalCount();
	})
