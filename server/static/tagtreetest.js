Ext.require([
    'Ext.data.*',
    'Ext.tip.*',
    'Ext.tree.*'
]);

Ext.define('Post', {
    extend: 'Ext.data.TreeModel',
    idProperty: 'id',
    fields: [{
        name: "id", /*id */
        convert: undefined
    }, {
        name: "name", /*name */
        convert: undefined
    }, {
        name: "path", /*name with level*/
        convert: undefined
    }]
});

Ext.onReady(function () {
    Ext.tip.QuickTipManager.init();

    var store = Ext.create('Ext.data.TreeStore', {
        model: 'Post',
        proxy: {
            type: 'ajax',
            reader: 'json',
            writer: 'json',
            url: '/api/view/'
        },
        lazyFill: true,
        listeners: {
            update: function (st, rec, op, modFldNames) {
                console.log(op);
                if (op == "edit" && modFldNames && modFldNames[0] == "name") {
                    this.sync();
                }
            }
        }
    });

    var tree = Ext.create('Ext.tree.Panel', {
        title: 'Tag Tree',
        width: '100%',
        height: 900,
        renderTo: Ext.getBody(),
        reserveScrollbar: true,
        collapsible: true,
        loadMask: true,
        useArrows: true,
        rootVisible: false,
        store: store,
        animate: false,
        plugins: 'cellediting',
        tbar: [
            {
                xtype: 'numberfield',
                anchor: '100%',
                name: 'treedepth',
                id: 'treedepth',
                fieldLabel: 'Tree depth level',
                value: 1,
                maxValue: 10,
                minValue: 1
            },
            {
                xtype: 'button',
                text: 'Set depth',
                handler: function (btn) {
                    store.getRootNode().removeAll();
                    store.load({
                        params: {
                            depth: Ext.getCmp('treedepth').value
                        },
                        callback: function(records, operation, success) {
                            // FIXME: ugly fix for properly sorted tree
                            store.getRootNode().collapse();
                            store.getRootNode().expand();
                        }
                    });
                }
            },
            {
                xtype: 'textfield',
                anchor: '100%',
                name: 'search',
                id: 'search',
                fieldLabel: 'Search by name'
            },
            {
                xtype: 'button',
                text: 'Search',
                handler: function (btn) {
                    store.getRootNode().removeAll();
                    store.load({
                        params: {
                            search: Ext.getCmp('search').value
                        },
                        callback: function(records, operation, success) {
                            // FIXME: ugly fix for properly sorted tree
                            store.getRootNode().collapse();
                            store.getRootNode().expand();
                        }
                    });
                }
            }
        ],
        listeners: {
            'rowcontextmenu': function (view, record, item, index, e, options) {
                function showMenu(view, record, item, index, e, options) {
                    e.stopEvent();
                    var menu = new Ext.menu.Menu({
                        items: [{
                            text: 'Delete',
                            handler: function () {
                                record.remove();
                                store.sync();
                            }
                        }]
                    }).showAt(e.getXY());
                }

                showMenu(view, record, item, index, e, options);
            }
        },
        columns: [
            {
                text: 'Level',
                sortable: false,
                dataIndex: 'nlevel'
            },
            {
                xtype: 'treecolumn', //this is so we know which column will show the tree
                text: 'Tree',
                flex: 2.5,
                sortable: true,
                dataIndex: 'name',
                editor: {
                    xtype: 'textfield',
                    allowBlank: false,
                    allowOnlyWhitespace: false
                }
            }]
    });
});
