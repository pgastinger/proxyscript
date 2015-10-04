# -*- coding: utf-8 -*-

import re
import IPy
import datetime


proxytemplate = """<?php header("Content-Type: application/x-ns-proxy-autoconfig");?>
var proxy;

proxy="PROXY %s:%d";

function FindProxyForURL(url, host) {
        //
        // only http, https, ftp are proxiable
        //
        if (!url.substring(0,5) == "http:" && !url.substring(0,6) == "https:" && !url.substring(0,4) == "ftp:") {
                return "DIRECT";
        }

        //
        // plain hostname without proxy
        //
        if (isPlainHostName(host)) {
                return "DIRECT";
        }

        //
        // localhost -> no proxy
        //
        if (isInNet(host, "127.0.0.0", "255.0.0.0")) {
                return "DIRECT";
        }
        //
        // 10.*.*.* -> no proxy
        //
        if (isInNet(host, "10.0.0.0", "255.0.0.0")) {
                return "DIRECT";
        }

        //
        // 172.16.*.* till 172.31.*.* -> no proxy
        //
        if (isInNet(host, "172.16.0.0", "255.240.0.0")) {
                return "DIRECT";
        }

        //
        // 192.168.*.* -> no proxy
        //
        if (isInNet(host, "192.168.0.0", "255.255.0.0")) {
                return "DIRECT";
        }

// start customer specific entries
%s
// end customer specific entries

        return proxy;
}
"""
entrytemplate_domain = """
        // %s/%s %s
        if (shExpMatch(url, "*%s*")) {
                return "DIRECT";
        }
"""
entrytemplate_ip = """
        // %s/%s %s
        if (isInNet(host, "%s","%s")) {
                return "DIRECT";
        }
"""


def index():
    """
    show all active customers
    """
    return dict()


def generate(id):
    """
    generate proxy scripts file (aka pac file)
    """
    ip_cidr_re = re.compile(r"(?<!\d\.)(?<!\d)(?:\d{1,3}\.){3}\d{1,3}/?\d{0,2}(?!\d|(?:\.\d))")

    customer = db((db.customers.isActive == True) & (db.customers.id == id)).select().first()
    if customer:
        entries = db((db.proxybypassentries.customer == id) & (db.proxybypassentries.customer == db.customers.id) &
                     (db.proxybypassentries.destination == db.destinations.id) &
                     (db.auth_user.id == db.proxybypassentries.addedby)).select()
        content = ""
        for entry in entries:
            m = ip_cidr_re.search(str(entry.destinations.destination))
            if m:
                n = IPy.IP(entry.destinations.destination)
                content += entrytemplate_ip % (entry.proxybypassentries.addedat.strftime("%d%b%Y"),
                                             entry.auth_user.username, entry.proxybypassentries.info, n.net(),
                                             n.netmask())
            else:
                content += entrytemplate_domain % (entry.proxybypassentries.addedat.strftime("%d%b%Y"),
                                                 entry.auth_user.username, entry.proxybypassentries.info,
                                                 entry.destinations.destination)
        custom_entries = db((db.customentries.customer == id) & (db.customentries.isActive == True)).select()
        for item in custom_entries:
            content += "\n"
            content += "\t//%s/%s %s\n" % (entry.proxybypassentries.addedat.strftime("%d%b%Y"),
                                         entry.auth_user.username, entry.proxybypassentries.info)
            content += item.entry
            content += "\n"
        return proxytemplate % (customer.proxyurl, customer.proxyport, content)
    else:
        return None


@auth.requires_login()
def pacTester():
    """
    testing pacfile
    needs  https://github.com/manugarg/pactester
    """
    try:
        import pacparser
    except ImportError:
        session.flash = T("pacparser is not installed")
        redirect(URL("default", "index"))

    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("PAC-File")))
    div0.append(SELECT(_name="pacfileid", *[OPTION(item.pacfile, _value=str(item.id))
                                            for item in db(db.customers.isActive).select()], _class="form-control",
                       requires=IS_IN_DB(db, 'customers.id', '%(pacfile)s')))
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("URL")))
    div1.append(INPUT(_name="url", _class="form-control", requires=IS_URL()))

    form.append(div0)
    form.append(div1)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Submit")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    ret = ""
    cust = ""
    url = ""
    logger.debug("1")
    if form.accepts(request, session, keepvalues=True):
        url = form.vars.url
        customer = db((db.customers.isActive == True) & (db.customers.id == form.vars.pacfileid)).select().first()
        if customer:
            import tempfile
            import os
            cust = customer.customer
            f = tempfile.NamedTemporaryFile(delete=False)
            fname = f.name
            f.write(generate(form.vars.pacfileid))
            f.close()
            try:
                ret = pacparser.just_find_proxy(fname, form.vars.url)
                logger.info("PAC-File %s successfully tested for url %s by %s" % (fname, form.vars.url,
                                                                                  auth.user.username))
            except:
                response.flash = T('Problem testing pacfile')
                logger.debug("Testing pacfile failed")
            else:
                response.flash = T('PAC-File %(pacfile)s successfully tested with url %(url)s',
                                   dict(pacfile=customer.pacfile, url=form.vars.url))
                os.remove(fname)
        else:
            response.flash = T('Problem testing pacfile')
    elif form.errors:
        response.flash = T('form has errors')
    return dict(form=form, ret=ret, customer=cust, url=url)


def showFile():
    """
    show pac file
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    if IS_INT_IN_RANGE(1, 100)(request.args[0])[1]:
        redirect(URL("index"))
    content = generate(request.args[0])
    customer = db(db.customers.id == request.args[0]).select().first()
    filename = ""
    if customer:
        filename = customer.pacfile
    if not content:
        redirect(URL("index"))
    return dict(filecontent=content, filename=filename)


def getFile():
    """
    get raw pac file, will be generated on the fly
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    customer = db((db.customers.isActive == True) & (db.customers.pacfile == request.args[0])).select().first()
    if customer:
        return generate(customer.id)
    else:
        session.flash = T("Could not generate PAC-File")
        redirect(URL("index"))


@auth.requires_login()
def multiChangesDestinations():
    """
    add specific destination to multiple customers
    pick destination first
    """
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Pick destination")))
    div0.append(SELECT(_name="destination", *[OPTION(item.destination, _value=str(item.id))
                                              for item in db(db.destinations.isActive).select()],
                       _class="form-control select2", requires=IS_IN_DB(db, 'destinations.id', '%(destination)s')))
    form.append(div0)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Next step")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        redirect(URL("multiChangesDestinationsEdit", args=form.vars.destination))
    elif form.errors:
        response.flash = T('form has errors')
    return dict(form=form)


@auth.requires_login()
def multiChangesDestinationsEdit():
    """
    add specific destination to multiple customers
    """

    if len(request.args) != 1:
        redirect(URL("multiChangesDestinations"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1]:
        redirect(URL("multiChangesDestinations"))

    form = FORM(_role="form")
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Info/Change")))
    div1.append(INPUT(_name="info", _class="form-control", requires=IS_NOT_EMPTY()))
    div0 = DIV(_class="form-group")
    destination = db(db.destinations.id == request.args[0]).select().first()
    customers = db(db.customers.isActive).select()
    entries = db((db.proxybypassentries.destination == request.args[0]) &
                 (db.customers.id == db.proxybypassentries.customer) &
                 (db.destinations.id == request.args[0])).select()
    for item in customers:
        checked = False
        for entry in entries:
            if entry.proxybypassentries.customer == item.id:
                checked = True
                break
        div0.append(INPUT(_name="customer%s" % item.id, _type="checkbox", value=checked))
        div0.append(LABEL(item.customer))
        div0.append(BR())

    form.append(div1)
    form.append(div0)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Commit changes")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        info = form.vars.info

# remove entries, which are not checked any more from database for customer
        for item in entries:
            key = "customer%s" % item.customers.id
            if key in form.vars and form.vars[key] is None:
                logger.info("Remove Destination %s for customer %s by %s with info %s" % (destination.destination,
                                                                                          item.customers.customer,
                                                                                          auth.user.username, info))
                db((db.proxybypassentries.destination == destination.id) &
                   (db.proxybypassentries.customer == item.customers.id)).delete()

        for item in form.vars:
            if item.startswith("customer") and form.vars[item]:
                # add entries if they are not yet in the database
                cid = item.replace("customer", "")
                if len(db((db.proxybypassentries.customer == cid) &
                                  (db.proxybypassentries.destination == destination.id)).select()) == 0:
                    logger.info("Adding Destination %s for customer %s by %s with info %s" %
                                (destination.destination, cid, auth.user.username, info))
                    db.proxybypassentries.insert(addedby=auth.user.id, addedat=datetime.datetime.now(),
                                                 info=info, customer=cid, destination=destination.id)
        session.flash = T("Changes successful")
        redirect(URL("default", "index"))
    elif form.errors:
        response.flash = T('form has errors')
    return dict(form=form, destination=destination.destination)


@auth.requires_login()
def multiChangesCustomers():
    """
    add specific customer to multiple destinations
    pick customer first
    """
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Pick customer")))
    div0.append(SELECT(_name="customer", *[OPTION(item.customer, _value=str(item.id))
                                           for item in db(db.customers.isActive).select()], _class="form-control",
                       requires=IS_IN_DB(db, 'customers.id', '%(customer)s')))
    form.append(div0)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Next step")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        redirect(URL("multiChangesCustomersEdit", args=form.vars.customer))
    elif form.errors:
        response.flash = T('form has errors')
    return dict(form=form)


@auth.requires_login()
def multiChangesCustomersEdit():
    """
    add specific customer to multiple destinations
    """
    if len(request.args) != 1:
        redirect(URL("multiChangesCustomers"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1]:
        redirect(URL("multiChangesCustomers"))

    form = FORM(_role="form")
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Info/Change")))
    div1.append(INPUT(_name="info", _class="form-control", requires=IS_NOT_EMPTY()))
    div0 = DIV(_class="form-group")
    customer = db(db.customers.id == request.args[0]).select().first()
    destinations = db(db.destinations.isActive).select()
    entries = db((db.proxybypassentries.customer == request.args[0]) &
                 (db.destinations.id == db.proxybypassentries.destination) &
                 (db.customers.id == request.args[0])).select()

    for item in destinations:
        checked = False
        for entry in entries:
            if entry.proxybypassentries.destination == item.id:
                checked = True
                break
        div0.append(INPUT(_name="destination%s" % item.id, _type="checkbox", value=checked))
        div0.append(LABEL(item.destination))
        div0.append(BR())

    form.append(div1)
    form.append(div0)

    form.append(INPUT(_class="btn", _type="submit", _value=T("Commit changes")))
    form.append(INPUT(_class="btn btn-danger", _type="reset", _value=T("Reset")))

    if form.accepts(request, session, keepvalues=True):
        info = form.vars.info

# remove entries, which are not checked any more from database for customer
        for item in entries:
            key = "destination%s" % item.destinations.id
            if key in form.vars and form.vars[key] is None:
                logger.info("Remove customer %s for destination %s by %s with info %s" % (customer.customer,
                                                                                          item.destinations.destination,
                                                                                          auth.user.username, info))
                db((db.proxybypassentries.customer == customer.id) &
                   (db.proxybypassentries.destination == item.destinations.id)).delete()

        for item in form.vars:
            if item.startswith("destination") and form.vars[item]:
                # add entries if they are not yet in the database
                did = item.replace("destination", "")
                if len(db((db.proxybypassentries.destination == did) &
                                  (db.proxybypassentries.customer == customer.id)).select()) == 0 :
                    logger.info("Adding customer %s for destination %s by %s with info %s" % (customer.customer,
                                                                                              did,
                                                                                              auth.user.username, info))
                    db.proxybypassentries.insert(addedby=auth.user.id, addedat=datetime.datetime.now(),
                                                 info=info, customer=customer.id, destination=did)

        session.flash = T("Changes successful")
        redirect(URL("default", "index"))
    elif form.errors:
        response.flash = T('form has errors')

    return dict(form=form, customer=customer.customer)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

