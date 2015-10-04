# -*- coding: utf-8 -*-

import datetime
import sys


@auth.requires_login()
def index():
    """
    show entries
    """
    btable = TABLE(_class="table table-striped table-bordered", _id="datatable")
    btableh = THEAD(TR(TH(T("Customer"), TH(T("Entry")), TH(T("info")), TH(T("addedat/addedby")), TH(T("Delete")))))
    btable.append(btableh)
    btableb = TBODY()

    for item in db((db.auth_user.id == db.proxybypassentries.addedby) &
                           (db.proxybypassentries.customer == db.customers.id) &
                           (db.proxybypassentries.destination == db.destinations.id)).select():
        btableb.append(TR(TD(A(item.customers.customer, _href=URL("customer", "index"))),
                          TD(A(item.destinations.destination, _href=URL("destination", "index"))),
                          TD(str(item.proxybypassentries.info)),
                          TD(str(item.proxybypassentries.addedat.strftime("%d%b%Y"))+"/"+str(item.auth_user.username)),
                          TD(A(SPAN(_class="glyphicon glyphicon-trash"),
                               _href=URL("delEntry", args=item.proxybypassentries.id)))))

    btable.append(btableb)
    return dict(form=btable)


@auth.requires_login()
def delEntry():
    """
    delete entry
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1]:
        redirect(URL("index"))
    entry = db((db.proxybypassentries.id == request.args[0]) & (db.proxybypassentries.customer == db.customers.id) &
               (db.proxybypassentries.destination == db.destinations.id)).select().first()
    ename = T("destination: %(destination)s customer: %(customer)s", dict(destination=entry.destinations.destination,
                                                                          customer=entry.customers.customer))
    form = FORM.confirm(T('Do you really want to delete entry %(entry)s?',
                          dict(entry=ename)))
    if form.accepted:
        try:
            db(db.proxybypassentries.id == request.args[0]).delete()
        except:
            response.flash = sys.exc_info()[1]
        else:
            logger.info("Deleting entry %s by %s" % (ename, auth.user.username))
            session.flash = T("Entry %(entry)s deleted successfully", dict(entry=ename))
            redirect(URL("index"))
    return dict(form=form, entry=ename)


@auth.requires_login()
def addEntry():
    """
    add entry
    """
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Customer")))
    div0.append(SELECT(_name="customer", *[OPTION(item.customer, _value=str(item.id))
                                           for item in db(db.customers.isActive).select()], _class="form-control",
                       requires=IS_IN_DB(db, 'customers.id', '%(customer)s')))

    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Destination")))
    div1.append(SELECT(_name="destination", *[OPTION(item.destination, _value=str(item.id))
                                              for item in db(db.destinations.isActive).select()], _class="form-control",
                       requires=IS_IN_DB(db, 'destinations.id', '%(destination)s')))

    div2 = DIV(_class="form-group")
    div2.append(LABEL(T("Info")))
    div2.append(INPUT(_name="info", _class="form-control", requires=IS_NOT_EMPTY()))

    form.append(div0)
    form.append(div1)
    form.append(div2)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Submit")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        if len(db((db.proxybypassentries.customer == form.vars.customer) &
                          (db.proxybypassentries.destination == form.vars.destination)).select()) > 0:
            response.flash = T("Combination of selected values not unique")
        else:
            try:
                id = db.proxybypassentries.insert(customer=form.vars.customer, destination=form.vars.destination,
                                                  info=form.vars.info, addedby=auth.user.id,
                                                  addedat=datetime.datetime.now())
            except:
                response.flash = sys.exc_info()[1]
            else:
                entry = db((db.proxybypassentries.id == id) & (db.proxybypassentries.customer == db.customers.id) &
                           (db.proxybypassentries.destination == db.destinations.id)).select().first()
                ename = T("destination: %(destination)s customer: %(customer)s",
                          dict(destination=entry.destinations.destination, customer=entry.customers.customer))
                logger.info("Added entry %s by %s" % (ename, auth.user.username))
                session.flash = T("Entry %(entry)s added successfully", dict(entry=ename))
                redirect(URL("index"))
    elif form.errors:
        response.flash = T('form has errors')

    return dict(form=form)

