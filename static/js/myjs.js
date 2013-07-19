/*!
 * my javascript library
 */


function splitpage(urltotal, urllist ,curindex, count, pagewin, usedata, showfun)
{
	$ .getJSON(urltotal, function(data){
			var totalpage = Math.floor((data["count"] + count - 1) / count);
			if(totalpage == 0){
			showfun(usedata);
			return;
			}
			if(curindex > totalpage){
			curindex = totalpage;
			}
			var begin = Math.floor((curindex - 1)/ pagewin) * pagewin + 1;
			$ (".splitpage").empty();
			if(begin > pagewin){
			var prevpage = begin - 1;
			var curli = $ ("<li class='pageindex' " + 
				"index='" + prevpage + "' rel='prev'>Prev</li>");
			$ (".splitpage").append(curli);
			}
			for(var i = 0 ; i < pagewin  ; ++i){
			var curitem = begin + i;
			if(curitem > totalpage){
			break;
			}
			var curli;
			if(curitem == curindex){
				curli = $ ("<li class='selectpage' " + 
						"index='" + curitem + "'>" + curitem + "</li>");
			}
			else {
				curli = $ ("<li class='pageindex' index='" + 
						curitem + "'>" + curitem + "</li>");
			}
			$ (".splitpage").append(curli);
			}
			if((totalpage - begin) >= pagewin){
				var nextpage = begin + pagewin;
				var curli = $ ("<li class='pageindex' " + 
						"index='" + nextpage + "' rel='next'>Next</li>");
				$ (".splitpage").append(curli);
			}
			var curitem = $ (".pageindex");
			curitem.bind("click", function(event){
					var index = $ (this).attr("index");
					splitpage(urltotal, urllist, index, 
						count, pagewin, usedata, showfun);
					});
			usedata.url = urllist + curindex + "/" + count;
			usedata.page = curindex;
			showfun(usedata);
	});
}

function setLiSelected(pattern, alist, pathname)
{
	var match = pattern.exec(pathname)
		if(match == null){
			return;
		}
	for(var i = 0 ; i < alist.length ; ++i){
		var matchitem = pattern.exec(alist[i].pathname);
		if(matchitem != null && matchitem[1] == match[1]){
			alist[i].parentNode.setAttribute("class", "selected");
			break;
		}
	}
}

function logoutclick()
{
	var logout = $("#logout");
	$.ajax({url: '/rest/user/logout',
			async: false,
			type: 'post',
			contentType: 'application/json',
			dataType: 'json',
			success: function(data){ window.location.href="/login"; }
			});
}

function setmenu()
{
	var alist = $("#my-navigation a");
	var pattern = /(^\/[^\/]*)/;
	setLiSelected(pattern, alist, location.pathname);
}

//----------------------------------------
// interface function
// blog
function getBlogCategory(usedata, useCategory)
{
	if(document.blogcategorylist){
		useCategory(usedata, document.blogcategorylist);
	}
	else {
	$ .ajax({url: "/rest/blog/category", 
			dataType: "json",
			async: false,
			success:function(data){
			var categorylist = new Array();
			$ .each(data, function(i){
				categorylist[data[i]["category_id"]] = {name: data[i]["name"],
				count: data[i]["count"],
				desc: data[i]["description"]};
				});
			document.blogcategorylist = categorylist;
			useCategory(usedata, document.blogcategorylist);
			}});
	}
}

function showBlogCategory()
{
	var alist = $(".widget-side ul#blogcategory li a");
	var pattern = /(^\/[^\/]*\/[0-9]+)/;
	setLiSelected(pattern, alist, location.pathname);
		/*
	getBlogCategory(null, function(usedata, categorylist){
			var curlis = "";
			$.each(categorylist, function(id){
				var curdata = categorylist[id];
				var curli = "<li><a href='/blog/" + id + "'>" + curdata["name"] + 
				" [" + curdata["count"] + "]</a></li>";
				curlis += curli;
				});
			$ ("#blogcategory").append($(curlis));
			var alist = $(".widget-side ul#blogcategory li a");
			var pattern = /(^\/[^\/]*\/[0-9]+)/;
			setLiSelected(pattern, alist, location.pathname);
			});
			*/
}

function showBlogList(usedata)
{
	var categoryid = usedata.categoryid;
	var page = usedata.page;
	var blogcount = usedata.blogcount;
	var bEdit = usedata.bEdit;
	getBlogCategory(usedata, function(usedata, categorylist){
			// add blog 
			var blogTitle = $("#blog-title");
			blogTitle.empty();
			blogTitle.append(categorylist[categoryid].name + "<span>" + 
				categorylist[categoryid].desc + 
				"</span><span class=\"morecontent\"><a href=\"/blog/" + 
				categoryid + "/\">更多日志&gt;&gt;</a></span>");

			var reqUrl = "/rest/blog/category/" + categoryid + 
			"/" + page + "/" + blogcount;
			$ .getJSON(reqUrl, function(data){
				// add blog content
				$ ("#blog-ul").empty();
				var curlis = "";
				$ .each(data, function(i){
					var curdata = data[i];
					var curcategory = '/blog/' + curdata["category_id"] + '/';
					var curli = "<li class='blog-li'>" +
					"<div class='blog-item'>" + 
					"<div class='blog-head'>" +
					"<a href='" + curcategory + 
					curdata['blogid'] + "'>" + curdata['title'] + "</a></div>" +
					"<div class='blog-attrs'><span class='blog-attr'>" + curdata['published'] + "</span>" +
					"<span class='blog-attr'>" + curdata['updated'] + "[U]</span>";
					if(bEdit){
						curli += "<span><a href='/manage/blog/" + curdata['blogid'] + 
						"'>编辑</a></span>"; 
					}
					curli += "<span class='categoryattr'><a href='" + curcategory + "'>" + 
					categorylist[curdata["category_id"]]["name"] + "</a></span></div>" +
					"<div class='blog-content'>" + curdata['summary'] + "</div>" +
					"</div></li>";
					curlis += curli;
					});
				$ ("#blog-ul").append($(curlis));
				});
	});
}

function showBlogContent(categoryid, blogid, bEdit)
{
	getBlogCategory(null, function(usedata, categorylist){
			// add blog 
			var blogTitle = $("#blog-title");
			blogTitle.empty();
			blogTitle.append(categorylist[categoryid].name + "<span>" + 
				categorylist[categoryid].desc + 
				"</span><span class=\"morecontent\"><a href=\"/blog/" + 
				categoryid + "/\">更多日志&gt;&gt;</a></span>");

				$.getJSON("/rest/blog/"+ blogid + "/", function(data){
					var curcategory = '/blog/' + categoryid + '/';
					var curli = "<li class='blog-li'>" +
					"<div class='blog-item'>" + 
					"<div class='blog-head'>" +
					"<a href='" + curcategory + data['blogid'] + "'>" +
					data['title'] + "</a></div>" +
					"<div class='blog-attrs'><span class='blog-attr'>" + data['published'] + "</span>" +
					"<span class='blog-attr'>" + data['updated'] + "[U]</span>"; 
					if (bEdit){
					curli += "<span class='blog-attr'><a href='/manage/blog/" + data['blogid'] + "'>编辑</a></span>"; 
					}
					curli += "<span class='categoryattr'><a href='" + curcategory + "'>" + 
					categorylist[categoryid]["name"] + "</a></span>" +
					"</div>" +
					"<div class='blog-content'>"+ data['content'] + "</div>" +
					"</div></li>";
					$ ("#blog-ul").empty();
					$ ("#blog-ul").append($(curli));
					});
	});
}

//--------------------------------------
// photo interface
function showphotoN(photocount)
{
	$ .getJSON("/rest/photo/list/1/" + photocount, function(data){
			$ ("#photo-ul").empty();
			var curlis = "";
			$ .each(data, function(i){
				var curdata = data[i];
				var curli = "<li class='photo-li'>" +
					"<div class='photo-list'><ul><li>" +
					"<a class='pirobox' href='" + curdata['big-photo'] + "'>" +
					"<img src='" + curdata['small-photo'] + 
					"' title='" + curdata['desc'] +
					"'></img></a></li>" +
					"<li>" + curdata['name'] + "</li>" +
					"<li>" + curdata['time'] + "</li>" + 
					"<li>" + curdata['updated'] + "[U]</li>" + 
					"</ul></div></li>";
				curlis += curli;
				});
			$ ("#photo-ul").append($(curlis));

			$ ().piroBox({my_speed: 400, //animation speed
				bg_alpha: 0.1, //background opacity
				slideShow : true, // true == slideshow on, false == slideshow off
				slideSpeed : 6, //slideshow duration in seconds(3 to 6 Recommended)
				close_all : '.piro_close,.piro_overlay'// add class .piro_overlay(with comma)if you want overlay click close piroBox
				});
			});
}

function showphoto(usedata)
{
	$ .getJSON(usedata.url, function(data){
			$ ("#photo-ul").empty();
			var curlis = "";
			$ .each(data, function(i){
				var curdata = data[i];
				var curli = "<li class='photo-li'>" +
					"<div class='photo-item'><ul><li>" +
					"<a class='pirobox' href='" + curdata['big-photo'] + "'>" +
					"<img src='" + curdata['small-photo'] + "' title='" + 
					curdata['desc'] + "'></img></a></li>" +
					"<li>" + curdata['name'] + "</li>" +
					"<li>" + curdata['time'] + "</li>" + 
					"<li>" + curdata['updated'] + "[U]</li>"; 
					if (usedata.bedit){
					curli += "<li><a href='/manage/photo/" + curdata['photoid'] + 
					"'>编辑</a></li>";  
					}
					curli += "</ul></div></li>";
				curlis += curli;
				});
			$ ("#photo-ul").append($(curlis));

			if($ (".piro_overlay").length > 0){
			$ (".piro_overlay").remove();
			$ (".pirobox_content").remove();
			$ ("#imgCache").remove();
			}
			$ ().piroBox({my_speed: 400, //animation speed
				bg_alpha: 0.1, //background opacity
				slideShow : true, // true == slideshow on, false == slideshow off
				slideSpeed : 6, //slideshow duration in seconds(3 to 6 Recommended)
				close_all : '.piro_close,.piro_overlay'// add class .piro_overlay(with comma)if you want overlay click close piroBox
				});
	});
}


//--------------------------------------
// mgr blog interface
function tinyMCEInit(){
	tinyMCE.init({
			// General options
mode : "textareas",
theme : "advanced",
plugins : "safari,spellchecker,pagebreak,style,layer,table,save,advhr,advimage,autosave,advlist,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template,wordcount",

// Theme options
theme_advanced_buttons1 : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect",
theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
theme_advanced_buttons4 : "insertlayer,moveforward,movebackward,absolute,|,styleprops,spellchecker,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,blockquote,pagebreak,restoredraft,|,insertfile,insertimage",
autosave_ask_before_unload : false,
oninit: setneworedit
});
}

function getblogcategoryforsel()
{
	// get blog category
	getBlogCategory(null, function(usedata, categorylist){
			var select = $(".blogform #blogcategory select");
			var options = "";
			$ .each(categorylist, function(id, value){
				var option = "<option value='" + id + "'>" + 
				value.name + "</option>";
				options += option;
				});
			select.append($(options));
			});
}

function setbtforedit(url)
{
	function responseblog(data){
		alert("提交成功");
	}

	$("#submit").bind("click", function(event){
			var title = $(".blogform input[name='title']").val();
			if(title.length==0){
			alert("标题不能为空!");
			return;
			}
			var rawcontent = tinyMCE.activeEditor.getContent({format : 'raw'});
			var summary = $(rawcontent).filter('p').eq(0).html();
			if(summary.length==0){
			alert("内容不能为空!");
			return;
			}
			var params = { "action": "update", "title": title,
			"summary": summary,
			"content": rawcontent,
			"privilege": $(".blogform #privilege select").val(),
			"category_id": $(".blogform #blogcategory select").val()};

			$.ajax({url: url+ setneworedit.blogid,
				type: 'post',
				contentType: 'application/json',
				dataType: 'json',
				data: JSON.stringify(params),
				success: responseblog
				});
	});
	$("#delete").bind("click", function(event){
			var ret = confirm("确认删除日志？");
			var params = { "action": "delete" };
			if(ret){
			$.ajax({url: url+ setneworedit.blogid,
				async: false,
				type: 'post',
				contentType: 'application/json',
				dataType: 'json',
				data: JSON.stringify(params),
				success: responseblog
				});
			window.location.href="/blog";
			}
			});
}

function setneworedit()
{
	var blogid = setneworedit.blogid;
	var url = "/rest/blog/";
	if (blogid){
		url += blogid;
		$ .getJSON(url, function(data){
				data = data[0]
				$(".blogform label[name='id']").text(blogid);
				$(".blogform input[name='title']").val(data["title"]);
				tinyMCE.activeEditor.setContent(data["content"]);
				$(".blogform #privilege option[value='" + data["privilege"] + "']").attr("selected", "selected");
				$(".blogform #blogcategory option[value='" + data["category_id"] + "']").attr("selected", "selected");
				});
	}
	else {
		var d = new Date();
		var newid = parseInt(d.getTime()/1000);
		setneworedit.blogid = newid;
		$(".blogform label[name='id']").text(newid + " [新]");
		$(".blogform input[name='delete']").attr("disabled", "disabled");
		$(".blogform #privilege option[value='-1']").attr("selected", "selected");
	}
}

function initmgrblog()
{
	tinyMCEInit();
	getblogcategoryforsel();
	var url = "/rest/blog/";
	setbtforedit(url);
}

// ------------------------------------------------
// login view
function refreshPic(img, url){
	var date = new Date();
	url += parseInt(date.getTime()/1000);
	img.attr("src", url);
}

function msgShow(msg, err){
	var msgSpan = $("#login-help span");
	msgSpan.hide();
	msgSpan.text(msg);
	if (err){
		msgSpan.addClass("errContent");
	}
	else{
		msgSpan.removeClass("errContent");
	}
	msgSpan.show();
}

function initLoginView(){
	var imgsrc = "/rest/user/authpicture/";
	var img = $("#authphoto");
	refreshPic(img, imgsrc);
	msgShow("输入认证信息登录。");

	$("#login-form input[name='user']").focus();
	// click change picture
	img.click(function(){
			refreshPic($(this), imgsrc);
			});

	$("#login-form input").bind("focus", 
			function(){
			msgShow("输入认证信息登录。");
			});

	function error(xhr, textStatus, errorThrown){
		var resp = JSON.parse(xhr.responseText);
		msgShow(resp.desc, "error");
		refreshPic(img, imgsrc);
	}

	function login(){
		var inputName = $("#login-form input[name='user']");
		var name= inputName.val();
		if(name.length==0){
			msgShow("用户名不能为空!", "error");
			return;
		}
		var passwd = $("#login-form input[name='passwd']").val();
		if(passwd.length==0){
			msgShow("密码不能为空!", "error");
			return;
		}
		var authstr = $("#login-form input[name='authcode']").val();
		if(authstr.length==0){
			msgShow("验证码不能为空!", "error");
			return;
		}
		var md5sum = hex_md5(passwd + authstr);
		var params = { "action": "login", "name": name, "authstr": authstr, "authcode": md5sum};

		// alert(JSON.stringify(params));
		$.ajax({url: "/rest/user/login",
				async: false,
				type: "post",
				contentType: "application/json",
				dataType: 'json',
				data: JSON.stringify(params),
				success: function(){window.location.href="/";},
				error: error
				});
	}
	$("#submit").bind('click', login);
	$("#login-form input").keydown(function(event){
			if (event.keyCode == 13){
			login();
			return false;
			}
			});
}

// ----------------------------------------------------
// manage photo 
function showimg(imgfile){
	var url = function(obj){
		if(obj){
			//ie
			if (client.browser.ie){
				obj.select();
				return document.selection.createRange().text;
			}
			//firefox
			else if(client.browser.firefox){
				if(obj.files)
				{
					if (obj.files.item(0).getAsDataURL){
						alert("url");
						return obj.files.item(0).getAsDataURL();
					}
					return window.URL.createObjectURL(obj.files.item(0));
				}
				return obj.value;
			}
			return obj.value;
		}
	}(imgfile);
	$("#imgphoto").attr("src", url); 
}

function modifyPhoto(url, photoid)
{
	url += photoid;
	$ .getJSON(url, function(data){
			$(".photoform label[name='id']").text(photoid);
			$(".photoform input[name='name']").val(data["name"]);
			$(".photoform textarea[name='description']").val(data["description"]);
			$("#imgphoto").attr("src", data["imgphoto"]);
			$(".photoform option[value='" + data["privilege"] + "']").attr("selected", "selected");
			});
	$(".photoform").attr("action", url);
	return photoid;
}

function addPhoto(url)
{
	var d = new Date();
	var newid = parseInt(d.getTime()/1000);
	url += newid;
	$(".photoform label[name='id']").text(newid + " [新]");
	$(".photoform input[name='delete']").attr("disabled", "disabled");
	$(".photoform option[value='-1']").attr("selected", "selected");
	$(".photoform").attr("action", url);
	return newid;
}

function mgrPhotoAction(url, photoid)
{
	if (!photoid){
		alert("photoid is error!");
		window.location.href="/";
		return false;
	}
	$("#submit").click(function(){
			var title = $(".photoform input[name='name']").val();
			if(title.length==0){
			alert("标题不能为空!");
			return false;
			}
			var desc = $(".photoform textarea[name='description']").val();
			if(desc.length==0){
			alert("内容不能为空!");
			return false;
			}
			//setTimeout(function(){window.location.href="/manage/photo/"}, 2000);
			});

	$("#delete").click(url+photoid, function(event){
			var ret = confirm("确认删除照片？");
			if(ret){
			var url = event.data + "/delete";
			$.ajax({url: url,
				async: false,
				type: 'post',
				contentType: 'application/json',
				dataType: 'json',
				success: function(data){
				alert("成功删除照片: " + data.desc);
				}
				});
			window.location.href="/manage/photo/";
			}
			});
	return true;
}

//-----------------------------------------
//  manage for resources
function addResource(url)
{
	$(".resform input[name='delete']").attr("disabled", "disabled");
	$(".resform option[value='-1']").attr("selected", "selected");
	$(".resform").attr("action", url + "add");
	return url;
}

function modifyResource(url, resourceid)
{
	url += resourceid;
	$ .getJSON(url, function(data){
			$(".resform input[name='id']").val(resourceid);
			$(".resform input[name='name']").val(data["name"]);
			$(".resform textarea[name='description']").val(data["desc"]);
			$(".resform[name='privilege'] option[value='" + data["privilege"] + "']").attr("selected", "selected");
			});
	$(".resform").attr("action", url);
	return url;
}

function mgrResAction(url)
{
	if (!url){
		alert("resource's url is error!");
		window.location.href="/";
		return false;
	}
	$("#submit").click(function(){
			var title = $(".resform input[name='name']").val();
			if(title.length==0){
			alert("标题不能为空!");
			return false;
			}
			var desc = $(".resform textarea[name='description']").val();
			if(desc.length==0){
			alert("内容不能为空!");
			return false;
			}
			//setTimeout(function(){window.location.href="/manage/resource/"}, 2000);
			});

	$("#delete").click(url, function(event){
			var ret = confirm("确认删除资源？");
			if(ret){
			var url = event.data + "/delete";
			$.ajax({url: url,
				async: false,
				type: 'post',
				contentType: 'application/json',
				dataType: 'json',
				success: function(data){
				alert("成功删除资源: " + data.desc);
				}
				});
			window.location.href="/manage/resource/";
			}
			});
	return true;
}

//-----------------------------------------
//user manage function
function initUserMgrBt(url)
{
	function response(data){
		alert("提交成功");
	}

	function error(xhr, textStatus, errorThrown){
		var resp = JSON.parse(xhr.responseText);
		alert(resp.desc);
		//refreshPic(img, imgsrc);
	}
	$("#submit").click(function(){
			var name = $("#userform input[name='name']").val();
			if(name.length==0){
			alert("用户名不能为空!");
			return;
			}
			var passwd = $("#userform input[name='passwd']").val();
			var verifypasswd = $("#userform input[name='verifypasswd']").val();
			if(passwd.length==0){
			alert("密码不能为空!");
			return;
			}
			else if(passwd!=verifypasswd){
			alert("密码确认不匹配");
			return;
			}
			var params = { "action": "update", "name": name,
			"passwd": passwd,
			"localname": $("#userform input[name='localname']").val(),
			"email": $("#userform input[name='email']").val(),
			"mobilephone": $("#userform input[name='mobilephone']").val(),
			"description": $("#userform textarea[name='description']").text(),
			"privilege": $("#userform select").val()};

			$.ajax({url: url,
					type: 'post',
					contentType: 'application/json',
					dataType: 'json',
					data: JSON.stringify(params),
					success: response,
					error: error
					});
	});
	$("#delete").click(function(){
			var ret = confirm("确认删除用户？");
			var params = { "action": "delete" };
			if(ret){
			$.ajax({url: url,
				async: false,
				type: 'post',
				contentType: 'application/json',
				dataType: 'json',
				data: JSON.stringify(params),
				success: response
				});
			window.location.href="/manage/user/";
			}
			});
}

function initUserMgr(url, userid)
{
	if (userid){
		url += userid;
		$ .getJSON(url, function(data){
				$("#userform input[name='id']").val(userid);
				$("#userform input[name='name']").val(data["name"]);
				$("#userform input[name='localname']").val(data["localname"]);
				$("#userform input[name='email']").val(data["email"]);
				$("#userform input[name='mobilephone']").val(data["mobilephone"]);
				$("#userform textarea[name='description']").text(data["description"]);
				$("#userform option[value='" + data["privilege"] + "']").attr("selected", "selected");
				});
	}
	else{
		$("#userform input[name='id']").val("[新]");
		$("#userform input[name='delete']").attr("disabled", "disabled");
		$("#userform option[value='0']").attr("selected", "selected");
	}
	return url;
}
