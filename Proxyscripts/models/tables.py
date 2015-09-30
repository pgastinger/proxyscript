# -*- coding: utf-8 -*-
db.define_table('destinations',
    Field('destination','string',length=50,unique=True),
    Field('info','string'),
    Field('addedby',db.auth_user),
    Field('addedat','datetime'),
    Field('isActive','boolean'),
    format='%(destination)s'
)

db.define_table('customers',
    Field('customer','string',length=50,unique=True),
    Field('proxyurl','string'),
    Field('proxyport','integer'),
    Field('pacfile','string',unique=True),
    Field('addedby',db.auth_user),
    Field('addedat','datetime'),
    Field('isActive','boolean'),
    format='%(customer)s'
)

db.define_table('proxybypassentries',
    Field('destination',db.destinations),
    Field('customer',db.customers),
    Field('info',"string"),
    Field('addedby',db.auth_user),
    Field('addedat','datetime'),
)

db.define_table('customentries',
    Field('customer',db.customers),
    Field('entry',"text"),
    Field('info','string'),
    Field('addedby',db.auth_user),
    Field('addedat','datetime'),
    Field('isActive','boolean'),
)
