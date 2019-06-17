function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    var $a = $('.edit');
    var $add = $('.add_type');
    var  $input_label = $(".input_label");
    var $remove = $('.remove_type')
    var $pop = $('.pop_con');
    var $cancel = $('.cancel');
    var $confirm = $('.confirm');
    var $error = $('.error_tip');
    var $input = $('.input_txt3');
    var sHandler = 'edit';
    var sId = 0;

    $a.click(function(){
        sHandler = 'edit';
        sId = $(this).parent().siblings().eq(0).html();
        $pop.find('h3').html('修改分类');
        $pop.find('.input_txt3').val($(this).parent().prev().html());
        $pop.show();
    });

    $add.click(function(){
        sHandler = 'add';
        $pop.find('h3').html('新增分类');
        $input.val('');
        $pop.show();
        $input_label.html("分类名称:");
    });
    $remove.click(function () {
        sHandler = 'remove';
        $pop.find('h3').html('删除分类');
        $input.val('');
        $pop.show();
        $input_label.html("输入分类id:");
    });

    $cancel.click(function(){
        $pop.hide();
        $error.hide();
    });

    $input.click(function(){
        $error.hide();
    });

    $confirm.click(function(){

        var params = {}
        if(sHandler=='edit')
        {
            var sVal = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            params = {
                "id": sId,
                "name": sVal,
            };
        }
        else if(sHandler=='remove')
        {
            var sId1 = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            params = {
                "id": sId1
            };
        }
        else
        {
            var sVal = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            params = {
                "name": sVal,
            }
        }

        // TODO 发起修改分类请求
            $.ajax({
            url:"/admin/news_type",
            method: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            contentType: "application/json",
            success: function (resp) {
                if (resp.errno == "0") {
                    // 刷新当前界面
                    location.reload();
                }else {
                    $error.html(resp.errmsg).show();
                }
            }
        })

    })
})