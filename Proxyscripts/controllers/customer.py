# -*- coding: utf-8 -*-

import datetime
import sys


@auth.requires_login()
def index():
    """
    index, show all customers
    """
    btable = TABLE(_class="table table-striped table-bordered", _id="datatable")
    btableh = THEAD(TR(TH(T("Customer")), TH(T("Proxy")), TH(T("PAC-File")), TH(T("Status")), TH(T("Entries")),
                       TH(T("addedat/addedby")), TH(T("Edit"), TH(T("Delete")))))
    btable.append(btableh)
    btableb = TBODY()

    for item in db(db.auth_user.id == db.customers.addedby).select():
        entrycount = db(db.proxybypassentries.customer == item.customers.id).count()
        status = SPAN(_class="glyphicon glyphicon-ok", _style="color:green")
        if not item.customers.isActive:
            status = SPAN(_class="glyphicon glyphicon-remove", _style="color:red")
        btableb.append(TR(TD(item.customers.customer), TD(item.customers.proxyurl+":"+str(item.customers.proxyport)),
                          TD(item.customers.pacfile), TD(status), TD(A(entrycount,
                                                                       _href=URL("default", "multiChangesCustomersEdit",
                                                                                 args=item.customers.id))),
                          TD(str(item.customers.addedat.strftime("%d%b%Y"))+"/"+str(item.auth_user.username)),
                          TD(A(SPAN(_class="glyphicon glyphicon-cog"),
                               _href=URL("editCustomer", args=item.customers.id))),
                          TD(A(SPAN(_class="glyphicon glyphicon-trash"),
                               _href=URL("delCustomer", args=item.customers.id)))))

    btable.append(btableb)
    return dict(form=btable)


@auth.requires_login()
def delCustomer():
    """
    delete customer by id
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1]:
        redirect(URL("index"))
    customer = db(db.customers.id == request.args[0]).select().first()
    cname = ""
    if customer:
        cname = customer.customer
    form = FORM.confirm(T('Do you really want to delete customer %s?') % cname)
    if form.accepted:
        try:
            db(db.customers.id == request.args[0]).delete()
        except:
            response.flash = sys.exc_info()[1]
        else:
            logger.info("Deleting customer %s by %s" % (cname, auth.user.username))
            session.flash = T("Customer %(customer)s deleted successfully", dict(customer=cname))
            redirect(URL("index"))
    return dict(form=form, customer=cname)


@auth.requires_login()
def addCustomer():
    """
    add customer
    """
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Customer (must be unique)")))
    div0.append(INPUT(_name="customername",
                      requires=IS_NOT_IN_DB(db, db.customers.customer,
                                            error_message=T("Customer name must be unique and not empty")),
                      _class="form-control"))
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Proxy-FQDN (e.g. proxy.r-services.at)")))
    div1.append(INPUT(_name="proxyfqdn", _class="form-control", requires=IS_URL(prepend_scheme=None)))
    div2 = DIV(_class="form-group")
    div2.append(LABEL(T("Proxy-Port (e.g. 57145)")))
    div2.append(INPUT(_name="proxyport", _class="form-control", requires=IS_INT_IN_RANGE(1, 65536)))
    div3 = DIV(_class="form-group")
    div3.append(LABEL(T("PAC-File (e.g. mwg_riz.php)")))
    div3.append(INPUT(_name="pacfile", _class="form-control",
                      requires=[IS_NOT_IN_DB(db, db.customers.pacfile),
                                IS_MATCH(".*\.php$", error_message=T("PAC-File name must end with .php"))]))
    div4 = DIV(_class="form-group")
    div4.append(LABEL(T("is active?"), INPUT(_name="isActive", _class="form-control", _type="checkbox", value=True)))

    form.append(div0)
    form.append(div1)
    form.append(div2)
    form.append(div3)
    form.append(div4)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Submit")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        try:
            db.customers.insert(customer=form.vars.customername, proxyurl=form.vars.proxyfqdn,
                                proxyport=form.vars.proxyport, pacfile=form.vars.pacfile, addedby=auth.user.id,
                                addedat=datetime.datetime.now(), isActive=form.vars.isActive)
        except:
            response.flash = sys.exc_info()[1]
        else:
            logger.info("Adding customer %s by %s" % (form.vars.customername, auth.user.username))
            session.flash = T("Customer %(customer)s added successfully", dict(customer=form.vars.customername))
            redirect(URL("index"))
    elif form.errors:
        response.flash = T('form has errors')
    return dict(form=form)


@auth.requires_login()
def editCustomer():
    """
    edit customer
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1]:
        redirect(URL("index"))
    customer = db(db.customers.id == request.args[0]).select().first()
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Customer (cannot be changed)")))
    div0.append(INPUT(_name="customername", _readonly=True, _class="form-control", _value=customer.customer))
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Proxy-FQDN (e.g. proxy.r-services.at)")))
    div1.append(INPUT(_name="proxyurl", _value=customer.proxyurl, _class="form-control",
                      requires=IS_URL(prepend_scheme=None)))
    div2 = DIV(_class="form-group")
    div2.append(LABEL(T("Proxy-Port (e.g. 57145)")))
    div2.append(INPUT(_name="proxyport", _value=customer.proxyport, _class="form-control",
                      requires=IS_INT_IN_RANGE(1, 65536)))
    div3 = DIV(_class="form-group")
    div3.append(LABEL(T("PAC-File (e.g. mwg_riz.php)")))
    div3.append(INPUT(_name="pacfile", _value=customer.pacfile, _class="form-control",
                      requires=[IS_MATCH(".*\.php$", error_message=T("PAC-File name must end with .php"))]))
    div4 = DIV(_class="form-group")
    div4.append(LABEL(T("is active?"), INPUT(_name="isActive", _class="form-control", _type="checkbox",
                                             value=customer.isActive)))

    form.append(div0)
    form.append(div1)
    form.append(div2)
    form.append(div3)
    form.append(div4)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Submit")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        try:
            db(db.customers.id == request.args[0]).update(proxyurl=form.vars.proxyurl, proxyport=form.vars.proxyport,
                                                        pacfile=form.vars.pacfile, isActive=form.vars.isActive)
        except:
            response.flash = sys.exc_info()[1]
        else:
            logger.info("Customer %s edited by %s" % (form.vars.customername, auth.user.username))
            session.flash = T("Customer %(customer)s edited successfully", dict(customer=form.vars.customername))
            redirect(URL("index"))
    elif form.errors:
        response.flash = T('form has errors')
    return dict(form=form)

