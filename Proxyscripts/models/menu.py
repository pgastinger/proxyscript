# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

response.logo = IMG(_class="navbar-brand",_src=URL("static/images","logo.png"))
response.title = "Proxy Script Generator"
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Peter Gastinger'
response.meta.description = 'Proxy Script Generator'
response.meta.keywords = 'PAC Proxy Script'
response.meta.generator = 'Web2py Web Framework'

response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (T('Edit'), False, URL() , [
        (T('Destinations'), False, URL('destination', 'index'), []),
        (T('Customers'), False, URL('customer', 'index'), []),
        (T('Entries'), False,URL('proxybypassentry', 'index'), []),
        (T('Custom-entries'), False,URL('customentry', 'index'), []),
    ]),
    (T('Multi-changes'), False, URL() , [
        (T("Add specific destination for multiple customers"), False,URL('default', 'multiChangesDestinations'), []),
        (T("Add specific customer for multiple destinations"), False,URL('default', 'multiChangesCustomers'), []),
    ]),
    (T('Tester'), False, URL('default','pacTester'), []),
    (T('Documentation'), False, URL() , [
        (T("Quick Start"), False,URL('documentation', 'howto'), []),
        (T("Database schema"), False,URL('documentation', 'database'), []),
    ]),
]
