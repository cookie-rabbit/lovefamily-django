$(".payOrderContainer")
	.on("input propertychange", function() {
		var nameL = $(".cartContent .name input").val().trim().replace(/\s/g, "").length;
		var cardL = $(".cartContent .card input").val().trim().replace(/\s/g, "").length;
		if (nameL > 0 && cardL > 0 ) {
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
	.on("click",".toPay",function(){
		var obj=formatObjVal({
			name:$(".cartContent .name input").val(),
			card:$(".cartContent .card input").val(),
			checked:$(".checkToAdd").hasClass("checked");
		});
	})
	.on("click",".checkToAdd",function(){
		$(".checkToAdd .check").toggleClass("checked");
	});
