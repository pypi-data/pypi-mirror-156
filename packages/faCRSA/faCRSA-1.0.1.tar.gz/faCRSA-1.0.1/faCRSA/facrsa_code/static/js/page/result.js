layui.use('table', function () {
    var table = layui.table;
    table.render({
        elem: '#result',
        url: "/api/getResult/" + document.getElementById('tid').getAttribute('value'),
        toolbar: '#toolbarDemo',
        title: 'Analysis Result',
        unresize: true,
        text: "System Error",
        cols: [
            [{
                field: 'tid',
                title: 'ID',
                width: 80,
                templet: '#xuhao',
                //fixed: 'left',
                unresize: true,
                sort: true,
                align: 'center',
                type: 'numbers'
            }, {
                field: 'ck_name',
                title: 'Folder Name',
                width: 80,
                //fixed: 'left',
                unresize: true,
                sort: true,
                align: 'center'
            }, {
                field: 'image',
                title: 'Image',
                //templet: '#imageUrl',
                width: 150,
                align: 'center'
            }, {
                field: 'out_image',
                title: 'Output Image',
                width: 150,
                templet: '#imageUrl',
                align: 'center'
            }, {
                field: 'trl',
                title: 'Total Root Length(mm)',
                width: 180,
                align: 'center',
                sort: true
            }, {
                field: 'tra',
                title: 'Total Root Area(mm²)',
                width: 180,
                align: 'center',
                sort: true
            }, {
                field: 'mrl',
                title: 'Primary Root Length(mm)',
                width: 180,
                sort: true,
                align: 'center'
            }, {
                field: 'mra',
                title: 'Primary Root Area(mm²)',
                width: 180,
                align: 'center',
                sort: true
            }, {
                field: 'rd',
                title: 'Root Depth(mm)',
                width: 120,
                align: 'center',
                sort: true
            }, {
                field: 'argr',
                title: 'Area Relative Growth Rate',
                width: 230,
                align: 'center',
                sort: true
            }, {
                field: 'lrgr',
                title: 'Length Relative Growth Rate',
                width: 230,
                align: 'center',
                sort: true
            }, {
                field: 'status',
                title: 'Status',
                width: 100,
                align: 'center',
                sort: true
            }]
        ],
        page: true
    });
    table.on('toolbar(test)', function (obj) {
    });
});