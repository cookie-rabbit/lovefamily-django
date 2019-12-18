$(".contentContainer")
	.on("click", ".type li", function() {
		$(".type li").removeClass("current");
		$(this).addClass("current");
		/* hot/new请求接口 */
		var req = {
			url: '',
			data: {
				value: {}
			},
			sucFun: function(res) {

			},
			errFun: function(err) {

			}
		};
		doAjax(req);
	})
	.on("click", ".more", function() {
		loadMore($(this));
	})
	.on("click", ".toCart", function() {
		console.log("加入购物车接口");
		return false;
	})
	.on("click", ".toBuy", function() {
		console.log("购买接口");
		return false;
	});
