layui.use('table', function () {
    var table = layui.table;
    table.render({
        elem: '#test',
        url: '/api/getMyTask',
        toolbar: '#toolbarDemo',
        defaultToolbar: ['filter', 'exports', 'print'],
        title: 'data table',
        text: "System Error",
        cols: [
            [{
                field: 'tid',
                title: 'ID',
                width: 80,
                templet: function (d) {
                    return d.LAY_TABLE_INDEX + 1
                },
                unresize: true,
                sort: true,
                align: 'center',
                type: 'numbers'
            }, {
                field: 'task_name',
                title: 'Name',
                align: 'center'
            }, {
                field: 'description',
                title: 'Description',
                align: 'center'
            }, {
                field: 'create_time',
                title: 'Creat Time',
                align: 'center',
                minWidth: 150,
                sort: true
            }, {
                field: 'update_time',
                title: 'Finish Time',
                sort: true,
                minWidth: 150,
                align: 'center'
            }, {
                field: 'status',
                title: 'Status',
                align: 'center',
                sort: true
            }, {
                fixed: 'right',
                title: 'Action',
                toolbar: '#barDemo',
                align: 'center',
            }]
        ],
        page: true
    });
    table.on('tool(test)', function (obj) {
        var data = obj.data;
        if (obj.event === 'del') {
            layer.msg('Confirm delete？', {
                time: 0
                , btn: ['yes', 'no']
                , yes: function (index) {
                    $.ajax({
                        type: "post",
                        url: "/api/delTask",
                        dataType: "json",
                        data: {tid: data.tid},
                        success: function (result) {
                            if (result == 200) {
                                layer.msg('Delete successfully', {
                                    icon: 6, time: 1000, end: function () {
                                        obj.del();
                                    }
                                });
                                layer.close(index);
                            } else {
                                layer.msg('Error！ Please try again!', {icon: 5});
                                layer.close(index);
                            }
                        }
                    });
                }
            });
        } else if (obj.event === 'view') {
            let test = '<div class="spinner-border spinner-border-sm text-success" role="status"><span class="visually-hidden">Loading...</span></div>';
            if (data.status == 2) {
                window.location.href = "/schedule/" + data.tid;
            } else if (data.status == 1) {
                window.location.href = "/result/" + data.tid;
            }
        }
    });

});