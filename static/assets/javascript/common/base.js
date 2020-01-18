/* mock测试接口 */
//var baseUrl = "http://10.168.2.93:3000/mock/21/api/";
//var baseUrl = "http://10.168.2.111:8000/api/"; //亚彤测试地址;
var baseUrl = "/api/"; //亚彤测试地址;


function doAjax(req) {
	$.ajax({
		url: req.url || baseUrl,
		async: req.async || true,
		cache: req.cache || true,
		crossDomain: true,
		method: req.method || "get",
		withCredentials: true,
		data: req.data || {},
		dataType: 'json',
		timeout: 5000,
		success: function(res) {
			console.log("地址" + req.url + "返回的结果是");
			console.log(res);
			req.sucFun(res) || function() {}
		},
		error: function(err) {
			console.log("err:");
			console.log(err);
			req.errFun(err) || function() {}
		},
	});
}

function loadMore(moreObj) {
	var req = {
		url: '',
		data: {
			count: 10,
			type: 'hot'
		},
		sucFun: function(res) {
			moreObj.before(res.name);
		},
		errFun: function(err) {

		}
	};
	doAjax(req);
}

function formatObjVal(obj) {
	for (me in obj) {
		obj[me] = obj[me].trim().replace(/\s/g, "");
	}
	return obj;
}
$(".notJump").on("click", function() {
	return false;
});

function getConfimDiv(content) {
	var sb = '	<div class="fixedDiv">';
	sb += '			<div class="confirmDiv">';
	sb += '				<p class="descConfirm">' + content + '</p>';
	sb += '				<p class="buttons">';
	sb += '					<span class="cancel">Cancel</span>';
	sb += '					<span class="confirm">Confirm</span>';
	sb += '				</p>';
	sb += '			</div>';
	sb += '		</div>';
	return sb;
}

function getToast01(content, time, href) {
	var time=time||2000;
	var sb = '	    <div class="fixedDiv">';
	sb += '				<div class="confirmDiv">';
	sb += '					<div class="toast01">';
	sb += '						<p>' + content + '</p>';
	sb += '					</div>';
	sb += '				</div>';
	sb += '			</div>';
	$(".container").after(sb);

	var height = $(".confirmDiv .toast01").height() / 2;

	$(".confirmDiv .toast01").css("margin-top", "-" + height + "px");
	setTimeout(function() {
		$(".fixedDiv").remove();
		if (href) {
			location.href = href;
		}
	}, time)
}
$(".container").on("click", ".fixedDiv .cancel", function() {
	$(".fixedDiv").remove();
});
$(".goBack,.searchHead").on("click", function() {
	history.go(-1)
})
