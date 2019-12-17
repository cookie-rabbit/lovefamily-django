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
$("header").on("click", ".search", function() {
	toSearch();
});
$(".toSearch").on("keydown", function(e) {
	var evt = window.event || e;
	if (evt.keyCode == 13) {
		toSearch();
	}
});

function toSearch() {
	var value = $(".toSearch").val().trim().replace(/\s/g, "");
	if (value.length > 0) {
      var req = {
      	url: '',
      	data: {
      		value: value
      	},
      	sucFun: function(res) {
			/* 跳转到搜索结果页面 */
      		location.href="";
      	},
      	errFun: function(err) {
      
      	}
      };
      doAjax(req);
	  
	} else {
		console.log("请输入关键词!!!");
	}

}
