$(".contentContainer")
	.on("click", ".type li", function() {
		$(".type li").removeClass("current");
		$(this).addClass("current");
		/* hot/new请求接口 */
		var req = {
			url: '',
			data: {
				value: value
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
