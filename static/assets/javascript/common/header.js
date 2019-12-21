$(".hasHover").hover(function(e) {
	var me = $(this);
	$(".hasHover").removeClass("current");
	me.addClass("current");

	$(".hasHover .ul").css("display", "none");
	me.find(".ul").slideDown("nomal");
	me.find(".name").addClass("spread");
}, function() {
	var me = $(this);
	$(".hasHover").removeClass("current");
	$(".hasHover .ul").slideUp("fast");
	me.find(".name").removeClass("spread");
});
$(".header")
	.on("click", ".search", function() {
		toSearch();
	})
	.on("click", ".toLog", function() {
		if ($(".loginDiv").css("display") == "block") {
			$(".loginDiv").slideUp("fast");
		} else {
			$(".loginDiv").slideDown("fast");
		}
		return false;
	});

$(".toSearch").on("keydown", function(e) {
	var evt = window.event || e;
	if (evt.keyCode == 13) {
		toSearch();
	}
});

function toSearch() {
	var keyword = $(".toSearch").val().trim().replace(/\s/g, "");
	if (keyword.length > 0) {
		/* 取消ajax请求模式 */
		/*var req = {
					url: baseUrl + 'goods/search/',
					data: {
						keyword: keyword
					},
					sucFun: function(res) {
						if (parseInt(res.errcode) === 0) {
							location.href = res.data.href;
						} else {
							$(".loginDiv p").html(res.errmsg).show();
						}

					},
					errFun: function(err) {
						$(".loginDiv p").html(res.errmsg).show();
					}
				};
				doAjax(req); */
		alert(keyword);
		location.href = ($(".toSearch").data("href") + "keyword=" + keyword);

	} else {
		console.log("请输入关键词!!!");
	}

}
$(".loginDiv")
	.on("click", ".submit", function() {
		var name = $(".loginDiv .name").val().trim();
		var pass = $(".loginDiv .password").val().trim();

		if (name.length > 0 && pass.length > 0) {
			$(".loginDiv p").hide();
			var req = {
				url: baseUrl + 'account/login/',
				data: {
					name: name,
					password: pass
				},
				method: "post",
				sucFun: function(res) {
					if (parseInt(res.errcode) === 0) {
						location.reload();
					} else {
						$(".loginDiv p").html(res.errmsg).show();
					}
				},
				errFun: function(err) {

				}
			};
			doAjax(req);

		} else {
			$(".loginDiv p").html("Mail or phone and password cannot be empty").show();
		}

	});
	$(".logout").on("click", function() {
		var req = {
			url: baseUrl + 'account/logout/',
			sucFun: function(res) {
				if (parseInt(res.errcode) === 0) {
					location.href=res.data.url;
				} else {
					$(".loginDiv p").html(res.errmsg).show();
				}
			},
			errFun: function(err) {

			}
		};
		doAjax(req);
	});
	$(".toIndex").on("click",function(){
		location.href=$(".header").data("href");
	});
