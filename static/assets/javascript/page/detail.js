$(function() {
	var timer = 0;
	var index = 0;
	if ($(".rollPic").length > 1) {
		var obj = $($(".rollPic")[0]).clone();
		$(".roll").append(obj);
		timer = setInterval(picLoop, 3000);

	} else {
		$(".prev,.next").addClass("hidden");
	}


	function picLoop() {
		index++;
		var nowIndex = index;
		if (nowIndex == $(".rollPic").length) {
			index = 0;
			$(".roll").css("left", "0");
			clearInterval(timer);
		}
		$(".roll").animate({
			"left": -442 * index
		}, 300);
		if (index == 0) {
			timer = setInterval(picLoop, 0);
		} else {
			clearInterval(timer);
			timer = setInterval(picLoop, 3000)
		}
	}

	$(".pics").hover(function() {
		clearInterval(timer);
	}, function() {
		timer = setInterval(picLoop, 3000);
	})

	$(".prev").click(function() {
		index--;
		if (index == -1) {
			index = $(".rollPic").length - 1;
			$(".roll").css("left", -442 * index + "px");
			index = index - 1;
		}
		$(".roll").animate({
			"left": -442 * index
		}, 300);

	})
	$(".next").click(function() {
		index++;
		if (index == $(".rollPic").length) {
			index = 1;
			$(".roll").css("left", "0");
		}
		$(".roll").animate({
			"left": -442 * index
		}, 300);
	})

	$(".goBack").on("click", function() {
		history.go(-1);
	});
})

$(".detailContainer")
	.on("click", ".add", function() {
		var me = $(this);
		var count = me.parents(".quantity").find(".count").val();
		count = parseInt(count) + 1;
		me.parents(".quantity").find(".count").val(count)
	})
	.on("click", ".sub", function() {
		var me = $(this);
		var count = me.parents(".quantity").find(".count").val();
		if (count > 1) {
			count = parseInt(count) - 1;
			me.parents(".quantity").find(".count").val(count);
		}
	});
$(".todo")
	.on("click", ".addCart", function() {
		var req = {
			url: baseUrl + 'carts/',
			data: {
				goods_id: $(this).data("id"),
				quantity: $(".quantity .count").val()
			},
			method: "post",
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					/* 修改购物车数量 */
				}
			},
			errFun: function(err) {

			}
		};
		doAjax(req);
		return false;
	})
	.on("click", ".buyNow", function() {
		var quantity = $(".quantity .count").val();
		/* 跳转需要携带数量 */
		location.href = $(this).data("href");
		return false;
	});;
