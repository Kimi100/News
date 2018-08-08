// 解析url中的查询字符串
function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(function () {
    // 页面加载完毕，获取新闻列表
    getNewsList(1)

    // 关注当前新闻作者
    $(".focus").click(function () {
        var user_id = $(this).attr('data-userid')
        var params = {
            "action": "follow",
            "user_id": user_id
        }
        $.ajax({
            url: "/news/followed_user",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 关注成功
                    var count = parseInt($(".follows b").html());
                    count++;
                    $(".follows b").html(count + "")
                    $(".focus").hide()
                    $(".focused").show()
                } else if (resp.errno == "4101") {
                    // 未登录，弹出登录框
                    $('.login_form_con').show();
                } else {
                    // 关注失败
                    alert(resp.errmsg)
                }
            }
        })
    })

// 取消关注当前新闻作者
    $(".focused").click(function () {
        var user_id = $(this).attr('data-userid')
        var params = {
            "action": "unfollow",
            "user_id": user_id
        }
        $.ajax({
            url: "/news/followed_user",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 取消关注成功
                    var count = parseInt($(".follows b").html());
                    count--;
                    $(".follows b").html(count + "")
                    $(".focus").show()
                    $(".focused").hide()
                } else if (resp.errno == "4101") {
                    // 未登录，弹出登录框
                    $('.login_form_con').show();
                } else {
                    // 取消关注失败
                    alert(resp.errmsg)
                }
            }
        })
    })

})

function getNewsList(page) {
    var query = decodeQuery()
    var params = {
        "p": page,
        "user_id": query["id"]
    }
    $.get("/user/other_news_list", params, function (resp) {
        if (resp.errno == "0") {
            // 先清空原有的数据
            $(".article_list").html("");
            // 拼接数据
            for (var i = 0; i < resp.data.news_list.length; i++) {
                var news = resp.data.news_list[i];
                var html = '<li><a href="/news/' + news.id + '" target="_blank">' + news.title + '</a><span>' + news.create_time + '</span></li>'
                // 添加数据
                $(".article_list").append(html)
            }
            // 设置页数和总页数
            $("#pagination").pagination("setPage", resp.data.current_page, resp.data.total_page);
        } else {
            alert(resp.errmsg)
        }
    })
}