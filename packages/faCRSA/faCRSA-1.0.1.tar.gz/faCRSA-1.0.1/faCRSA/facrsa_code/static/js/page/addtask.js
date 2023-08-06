layui.use(['upload', 'element', 'layer'], function () {
    var $ = layui.jquery,
        upload = layui.upload,
        element = layui.element,
        layer = layui.layer;

    var uploadListIns = upload.render({
        elem: '#selectImg',
        elemList: $('#imgList'),
        url: '/uploadImg',
        accept: 'file',
        multiple: true,
        number: 80,
        auto: true,
        drag: true,
        exts: 'jpg|png|jpeg',
        before: function (obj) {
            var files = this.files = obj.pushFile(); // layui文档标注这是一个文件队列，(每次选定文件都会往其中添加)
            layer.msg('Uploading', {icon: 16, time: 0});
            var fileLength = Object.keys(files).length;
        },
        choose: function (obj) {
            var that = this;
            var files = this.files = obj.pushFile(); //将每次选择的文件追加到文件队列
            $("#submitTaskForm").attr("disabled", false);
            obj.preview(function (index, file, result) {
                var tr = $(['<tr id="upload-' + index + '">', '<td>' + file.name +
                '</td>', '<td>' + (file.size / 1014).toFixed(1) + 'kb</td>',
                    '<td>',
                    '<button class="layui-btn layui-btn-xs demo-reload layui-hide">Re-upload</button>',
                    "<button class='btn btn-outline-danger btn-sm waves-effect demo-delete'>Delete</button>",
                    '</td>', '</tr>'
                ].join(''));
                //单个重传
                tr.find('.demo-reload').on('click', function () {
                    obj.upload(index, file);
                });
                //删除
                tr.find('.demo-delete').on('click', function () {
                    delete files[index]; //删除对应的文件
                    $.ajax({
                        type: "post",
                        url: "/api/delImg",
                        data: {
                            img: file.name
                        },
                        dataType: "json",
                        success: function (result) {
                            if (result.code == 200) {
                                layer.msg('Delete Successful');
                            } else {
                                layer.msg('Delete Error');
                            }
                        }
                    });
                    tr.remove();
                    uploadListIns.config.elem.next()[0].value =
                        ''; //清空 input file 值，以免删除后出现同名文件不可选
                    let fileLength = Object.keys(files).length;
                    if (fileLength <= 0) {
                        $("#submitTaskForm").attr("disabled", true);
                    }
                });
                that.elemList.append(tr);
                //element.render('progress'); //渲染新加的进度条组件
            });

        },
        allDone: function (obj) {
            console.log((obj))
            if (obj.failed == 0) { //上传成功
                layer.msg('Upload Successful');
                $("#submitTaskForm").attr("disabled", false);
                return;
            } else {
                layer.msg('Upload Error');
                return;
            }
        },
        error: function (index, upload) { //错误回调
            var that = this;
            var tr = that.elemList.find('tr#upload-' + index),
                tds = tr.children();
            tds.eq(3).find('.demo-reload').removeClass('layui-hide'); //显示重传
        },
        progress: function (n, elem, e, index) { //注意：index 参数为 layui 2.6.6 新增
            element.progress('progress-demo-' + index, n + '%'); //执行进度条。n 即为返回的进度百分比
        }
    });
});


$("#submitTaskForm").click(function () {
    'use strict';
    var addTaskForm = $('#addTaskFrom');
    if (addTaskForm.length) {
        addTaskForm.validate({
            rules: {
                'name': {
                    required: true,
                    maxlength: 20
                },
                'des': {
                    required: true,
                    maxlength: 20
                },
                'mail': {
                    required: true,
                    email: true
                },
                'cf': {
                    required: true,
                    number: true
                }
            },
            submitHandler: function (form) {
                addTask();
            }
        });
    }
})

function addTask() {
    $.ajax({
        type: "post",
        url: "/api/addTask",
        dataType: "json",
        data: $('#addTaskFrom').serialize(),
        success: function (result) {
            if (result.code == 200) {
                layer.msg('Submitted successfully', {
                    icon: 6, end: function () {
                        window.location.href =
                            "/schedule/"+result.tid;
                    }
                });

            } else {
                layer.msg('Error！ Please try again!', {icon: 5});
            }
        }
    });
}
