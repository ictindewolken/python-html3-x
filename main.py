#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from google.appengine.ext import ndb
from string import Template

class Todo(ndb.Model):
    description = ndb.StringProperty(indexed = False)
    done = ndb.BooleanProperty(indexed = False)

todoHtml = """
<!DOCTYPE html>
<html>
  <head>
    <title>$title</title>
  </head>
  <body>
    $items
    $newItem
  </body>
</html>
"""

itemHtml = """
<li>
  <form action="/todos/$id" method="POST">
    <input type="checkbox" name="done" value="True" $checked>
    <input type="text" name="descr" value="$descr">
    <button type="submit">update</button>
  </form>
</li>
"""

listHtml = """
<ul>
  $items
</ul>
"""

newItemHtml = """
<form action="/todos" method="POST">
  <input type="checkbox" name="done" value="OK">
  <input type="text" name="descr" value="...tbd...">
  <button type="submit">create</button>
</form>
"""

def makeHtml(items):
    mapping = {"title": "todo-list", "body": "<h3>GET list: empty</h3>"}
    itemsHtml = ""
    if len(items) > 0:
        for i in range(len(items)):
            itemsHtml = itemsHtml + \
                Template(itemHtml).substitute(id = items[i].key.id(),
                         descr = items[i].description,
                         checked = "checked" if items[i].done else "" )
        itemsHtml = Template(listHtml).substitute(items = itemsHtml)
    else:
        pass
    mapping["items"] = itemsHtml
    mapping["newItem"] = newItemHtml
    html = Template(todoHtml).substitute(mapping)
    return html

class TodoListHandler(webapp2.RequestHandler):
    def get(self):
        todoQuery = Todo().query()
        items = todoQuery.fetch()
        self.response.write(makeHtml(items))

    def post(self):
        item = Todo(description = self.request.get("descr"), done = False)
        key = item.put()
        print("POST list" + " create: " + str(key))
        todoQuery = Todo().query()
        items = todoQuery.fetch()
        print("#items: " + str(len(items)))
        self.response.write(makeHtml(items))

class TodoItemHandler(webapp2.RequestHandler):
    def get(self, id):
        self.response.write("GET item " + str(id))

    def post(self, id):
        itemKey = ndb.Key("Todo", int(id))
        item = itemKey.get()
        item.description = self.request.get("descr")
        print("done: " + self.request.get("done"))
        if self.request.get("done") ==  "True":
            item.done = True
        else:
            item.done = False
        item.put()
        print("POST item " + str(item))
        todoQuery = Todo().query()
        items = todoQuery.fetch()
        self.response.write(makeHtml(items))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world from Python (c9)!')

app = webapp2.WSGIApplication([
    (r'/', MainHandler),
    (r'/todos', TodoListHandler),
    (r'/todos/(\d+)', TodoItemHandler)
], debug=True)
