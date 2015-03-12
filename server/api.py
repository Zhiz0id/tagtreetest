#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yura Beznos'


import web
import simplejson as json
import psycopg2

DSN = "dbname='dmoz' user='dmoz' host='127.0.0.1' password='dmoz'"

urls = (
    '/', 'index',
    '/api/view/', 'view',
)

# Redirect to index
class index:
    def GET(self):
        index = """<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>
            Tag Tree Task
        </title>
        <link rel="stylesheet" type="text/css" href="static/ext-5.1.0/examples/shared/example.css">

    <!-- GC -->
        <script type="text/javascript" src="static/ext-5.1.0/examples/shared/include-ext.js"></script>
        <script type="text/javascript" src="static/ext-5.1.0/examples/shared/options-toolbar.js"></script>
        <script type="text/javascript" src="static/tagtreetest.js"></script>
    </head>
    <body>
        <div id="tree-example"></div>
    </body>
</html>"""
        web.header('Content-Type', 'text/html')
        return index

# Our simple API
class view:
    def get_node(self, node, depth, search):
        """
        Get list of children of node by id

        :param node: id for tag in table
        :param depth: how deep we need our tree
        :param search search query
        :return: result with list of children
        """
        _depth = depth
        try:
            conn = psycopg2.connect(DSN)
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()

        result = []
        if search:
            cur.execute("""SELECT path FROM dmoz WHERE name = '%s' ORDER BY path""" % search)
            path = []
            for _path in cur:
                path.append(_path)

            def leaf(r, level, _id, _name, _path, _nlevel):
                _expanded = False
                if _name != search:
                    _expanded = True

                if level == 1:
                    r.append({'id': _id, 'name': _name, 'path': _path, 'nlevel': _nlevel, 'expanded': _expanded})
                elif level > 1:
                    if 'children' not in r[-1]:
                        r[-1]['children'] = []
                    leaf(r[-1]['children'], level - 1, _id, _name, _path, _nlevel)

            if len(path) > 0:
                request = """SELECT id,name,path,nlevel(path) FROM dmoz WHERE path @> '%s' """ % path[0]
                del(path[0])
                if len(path) > 0:
                    for _p in path:
                        request += """OR path @> '%s' """ %_p
                request += """ORDER BY path"""
                print request
                cur.execute(request)

            for _id, _name, _path, _nlevel in cur:
                leaf(result, _nlevel, _id, _name, _path, _nlevel)

            return json.dumps(result)

        if node == 'root':

            cur.execute("""SELECT id,name,path,nlevel(path) FROM dmoz WHERE path ~ '*{0,%s}' ORDER BY path""" % depth)

            def leaf(r, level, _id, _name, _path, _nlevel):
                _expanded = False
                if depth > _nlevel:
                    _expanded = True
                if level == 1 and _depth == 1:
                    r.append({'id': _id, 'name': _name, 'path': _path, 'nlevel': _nlevel, 'expanded': _expanded})
                elif level == 1 and _depth > 1:
                    r.append({'id': _id, 'name': _name, 'path': _path, 'nlevel': _nlevel, 'expanded': _expanded})
                elif level > 1:
                    if 'children' not in r[-1]:
                        r[-1]['children'] = []
                    leaf(r[-1]['children'], level - 1, _id, _name, _path, _nlevel)

            for _id, _name, _path, _nlevel in cur:
                _depth = _nlevel
                leaf(result, _nlevel, _id, _name, _path, _nlevel)

        else:
            cur.execute("""SELECT * from dmoz where id = %s""" % node)
            for _id, _name, _path in cur:
                path = _path

            cur.execute("""SELECT id,name,path,nlevel(path) FROM dmoz WHERE path ~ '%s.*{1}' ORDER BY path""" % path)
            for _id, _name, _path, _nlevel in cur:
                result.append({'id': _id, 'name': _name, 'path': _path, 'nlevel': _nlevel})

        return json.dumps(result)

    def GET(self):
        node = 'root'
        depth = 1
        search = False

        if 'node' in web.input():
            node = web.input()['node']
        if 'depth' in web.input():
            depth = int(web.input()['depth'])
        if 'search' in web.input():
            search = web.input()['search']

        return self.get_node(node, depth, search)

    def POST(self):
        try:
            data = json.loads(web.data())
        except:
            data = {}

        _id = 0
        _name = False
        if 'id' in data:
            _id = int(data['id'])

        if 'name' in data and len(data['name']) > 0:
            _name = data['name'].translate(None, "'\"")

        print data, _id, _name
        try:
            conn = psycopg2.connect(DSN)
        except:
            print "I am unable to connect to the database"

        cur = conn.cursor()

        result = []

        if _id == 0 and _name is False:
            return ''
        elif _id > 0 and _name is False:
            try:
                cur.execute("""SELECT path from dmoz where id = %s""" % _id)
                for _path in cur:
                    path = _path

                cur.execute("""DELETE FROM dmoz WHERE path ~ '%s.*'""" %(path))
                conn.commit()
            except:
                print 'I am unable to delete from database'
            return result
        else:
            try:
                cur.execute("""UPDATE dmoz SET name = '%s' WHERE id = %s""" % (_name, _id))
                conn.commit()
                cur.execute("""SELECT id,name,path,nlevel(path) FROM dmoz WHERE id = %s""" % _id)
                for _id, _name, _path, _nlevel in cur:
                    result.append({'id': _id, 'name': _name, 'path': _path, 'nlevel': _nlevel})
                return json.dumps(result)
            except:
                return result
        return result


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()