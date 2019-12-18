/* 临时测试接口 */
var baseUrl = "http://10.168.2.93:3000/mock/12/account/info";


function doAjax(req) {
	$.ajax({
		url: req.url||baseUrl,
		async: req.async || true,
		cache: req.cache || true,
		contentType: req.contentType || 'application/x-www-form-urlencoded',
		method: req.method || "get",
		data: req.data || {},

		success: function(res) {
			if (res.errcode === 0) {
				req.sucFun(res.result) || function() {}
			}
		},
		error: function(err) {
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
$(".notJump").on("click",function(){
	return false;
});


