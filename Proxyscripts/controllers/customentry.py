# -*- coding: utf-8 -*-

import datetime
import sys


@auth.requires_login()
def index():
    """
    show entries
    """
    btable = TABLE(_class="table table-striped table-bordered", _id="datatable")
    btableh = THEAD(TR(TH(T("Customer")), TH(T("Custom-Entry")), TH(T("Info")), TH(T("Status")),
                       TH(T("addedat/addedby")), TH(T("Edit"), TH(T("Delete")))))
    btable.append(btableh)
    btableb = TBODY()

    for item in db((db.auth_user.id == db.customentries.addedby) & (db.customers.id == db.customentries.customer))\
            .select():
        status = SPAN(_class="glyphicon glyphicon-ok", _style="color:green")
        if not item.customentries.isActive:
            status = SPAN(_class="glyphicon glyphicon-remove", _style="color:red")
        btableb.append(TR(TD(item.customers.customer), TD(PRE(item.customentries.entry)), TD(item.customentries.info),
                          TD(status), TD(str(item.customentries.addedat.strftime("%d%b%Y")) + "/" +
                                        str(item.auth_user.username)), TD(A(SPAN(_class="glyphicon glyphicon-cog"),
                                                                            _href=URL("editCustomEntry",
                                                                                      args=item.customentries.id))),
                          TD(A(SPAN(_class="glyphicon glyphicon-trash"),
                               _href=URL("delCustomEntry", args=item.customentries.id)))))

    btable.append(btableb)
    return dict(form=btable)


@auth.requires_login()
def delCustomEntry():
    """
    delete custom entries
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1]:
        redirect(URL("index"))
    customentry = db(db.customentries.id == request.args[0]).select().first()
    dname = ""
    if customentry:
        dname = customentry.id
    form = FORM.confirm(T('Custom entry id %(id)s wirklich löschen?', dict(id=dname)))
    if form.accepted:
        try:
            db(db.customentries.id == request.args[0]).delete()
        except:
            response.flash = sys.exc_info()[1]
        else:
            logger.info("Deleting custom entry %s by %s" % (dname, auth.user.username))
            session.flash = T("Custom entry %(id)s deleted successfully", dict(id=dname))
            redirect(URL("index"))
    return dict(form=form, customentry=dname)


@auth.requires_login()
def addCustomEntry():
    """
    add custom entry
    """
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Customer")))
    div0.append(SELECT(_name="customer", *[OPTION(item.customer, _value=str(item.id))
                                          for item in db(db.customers.isActive).select()],
                       _class="form-control", requires=IS_IN_DB(db, 'customers.id', '%(customer)s')))
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Custom entry")))
    div1.append(TEXTAREA(_name="customentry", _class="form-control", requires=IS_NOT_EMPTY()))
    div2 = DIV(_class="form-group")
    div2.append(LABEL(T("Info")))
    div2.append(INPUT(_name="info", _class="form-control", requires=IS_NOT_EMPTY()))
    div3 = DIV(_class="form-group")
    div3.append(LABEL(T("is active?"), INPUT(_name="isActive", _class="form-control", _type="checkbox", value=True)))

    form.append(div0)
    form.append(div1)
    form.append(div2)
    form.append(div3)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Submit")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        try:
            id = db.customentries.insert(customer=form.vars.customer, info=form.vars.info, isActive=form.vars.isActive,
                                         entry=form.vars.customentry, addedby=auth.user.id,
                                         addedat=datetime.datetime.now())
        except:
            response.flash = sys.exc_info()[1]
        else:
            session.flash = T("Custom entry %(id)s added successfully", dict(id=id))
            logger.info("Added custom entry %s by %s" % (id, auth.user.username))
            redirect(URL("index"))
    elif form.errors:
        response.flash = T('form has errors')

    return dict(form=form)


@auth.requires_login()
def editCustomEntry():
    """
    edit custom entry
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1]:
        redirect(URL("index"))
    customentry = db((db.customers.id == db.customentries.customer) & (db.customentries.id == request.args[0])).\
        select().first()
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Customer")))
    div0.append(INPUT(_name="destinationname", _value=customentry.customers.customer, requires=IS_NOT_EMPTY(),
                      _class="form-control", _readonly="readonly"))
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Entry (Valid JavaScript-code necessary)")))
    div1.append(TEXTAREA(customentry.customentries.entry, _name="entry", _class="form-control",
                         requires=IS_NOT_EMPTY()))
    div2 = DIV(_class="form-group")
    div2.append(LABEL(T("Info")))
    div2.append(INPUT(_name="info", _value=customentry.customentries.info, _class="form-control"))
    div3 = DIV(_class="form-group")
    div3.append(LABEL(T("is active?"), INPUT(_name="isActive", _class="form-control", _type="checkbox",
                                             value=customentry.customentries.isActive)))

    form.append(div0)
    form.append(div1)
    form.append(div2)
    form.append(div3)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Submit")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        try:
            db(db.customentries.id == request.args[0]).update(info=form.vars.info, isActive=form.vars.isActive,
                                                              entry=form.vars.entry, addedby=auth.user.id,
                                                              addedat=datetime.datetime.now())
        except:
            response.flash = sys.exc_info()[1]
        else:
            session.flash = T("Custom entry %(id)s edited successfully", dict(id=form.vars.destinationname))
            logger.info("Custom entry %s edited by %s" % (id, auth.user.username))
            redirect(URL("index"))
    elif form.errors:
        response.flash = T('form has errors')

    return dict(form=form)
