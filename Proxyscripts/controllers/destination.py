# -*- coding: utf-8 -*-

import datetime
import sys

@auth.requires_login()
def index():
    """
    show destinations
    """
    btable = TABLE(_class="table table-striped table-bordered",_id="datatable")
    btableh = THEAD(TR(TH(T("Destination")),TH(T("Info")),TH(T("Entries")),TH(T("Status")),TH(T("addedat/addedby")),TH(T("Edit"),TH(T("Delete")))))
    btable.append(btableh)
    btableb = TBODY()

    for item in db(db.auth_user.id==db.destinations.addedby).select():
        entrycount = db(db.proxybypassentries.destination==item.destinations.id).count()
        status = SPAN(_class="glyphicon glyphicon-ok",_style="color:green")
        if not item.destinations.isActive:
            status = SPAN(_class="glyphicon glyphicon-remove",_style="color:red")
        btableb.append(TR(TD(item.destinations.destination),TD(item.destinations.info),TD(A(entrycount,_href=URL("default","multiChangesDestinationsEdit",args=item.destinations.id))),TD(status),TD(str(item.destinations.addedat.strftime("%d%b%Y"))+"/"+str(item.auth_user.username)),TD(A(SPAN(_class="glyphicon glyphicon-cog"),_href=URL("editDestination",args=item.destinations.id))),TD(A(SPAN(_class="glyphicon glyphicon-trash"),_href=URL("delDestination",args=item.destinations.id)))))

    btable.append(btableb)
    return dict(form=btable)

@auth.requires_login()
def delDestination():
    """
    delete destination
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1] != None:
        redirect(URL("index"))
    destination = db(db.destinations.id==request.args[0]).select().first()
    dname = ""
    if destination:
        dname = destination.destination
    form = FORM.confirm(T('Do you really want to delete destination %(destination)s?',dict(destination=dname)))
    if form.accepted:
        try:
            db(db.destinations.id==request.args[0]).delete()
        except:
            response.flash =  sys.exc_info()[1]
        else:
            logger.info("Deleting destination %s by %s"%(dname,auth.user.username))
            session.flash=T("Destination %(destination)s deleted successfully",dict(destination=dname))
            redirect(URL("index"))
    return dict(form=form,destination=dname)

@auth.requires_login()
def addDestination():
    """
    add destination
    """
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Destination (must be unique)")))
    div0.append(INPUT(_name="destinationname",requires = [IS_NOT_IN_DB(db,db.destinations.destination),ANY_OF([IS_URL(prepend_scheme=None)])],_class="form-control"))
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Info")))
    div1.append(INPUT(_name="info",_class="form-control",requires=IS_NOT_EMPTY()))
    div2 = DIV(_class="form-group")
    div2.append(LABEL(T("is active?"),INPUT(_name="isActive",_class="form-control",_type="checkbox", value=True)))

    form.append(div0)
    form.append(div1)
    form.append(div2)

    form.append(INPUT(_class="btn",_type="submit",_value=T("Submit")))
    form.append(INPUT(_class="btn btn-danger",_type="reset",_value=T("Reset")))

    if form.accepts(request,session,keepvalues=True):
        try:
            db.destinations.insert(destination=form.vars.destinationname,info=form.vars.info,isActive=form.vars.isActive,addedby=auth.user.id,addedat=datetime.datetime.now())
        except:
            response.flash =  sys.exc_info()[1]
        else:
            logger.info("Destination %s added successfully by %s"%(form.vars.destinationname,auth.user.username))
            session.flash = T("Destination %(destination)s added successfully",dict(destination=form.vars.destinationname))
            redirect(URL("index"))
    elif form.errors:
        response.flash = T('form has errors')

    return dict(form = form)

@auth.requires_login()
def editDestination():
    """
    edit destination
    """
    if len(request.args) != 1:
        redirect(URL("index"))
    if IS_INT_IN_RANGE(1, 1000)(request.args[0])[1] != None:
        redirect(URL("index"))
    destination = db(db.destinations.id==request.args[0]).select().first()
    form = FORM(_role="form")
    div0 = DIV(_class="form-group")
    div0.append(LABEL(T("Destination (must be unique)")))
    div0.append(INPUT(_name="destinationname",_value=destination.destination,requires = IS_URL(prepend_scheme=None),_class="form-control"))
    div1 = DIV(_class="form-group")
    div1.append(LABEL(T("Info")))
    div1.append(INPUT(_name="info",_value=destination.info,_class="form-control", requires = IS_NOT_EMPTY()))
    div2 = DIV(_class="form-group")
    div2.append(LABEL(T("is active?"),INPUT(_name="isActive",_class="form-control",_type="checkbox", value=destination.isActive)))

    form.append(div0)
    form.append(div1)
    form.append(div2)

    form.append(INPUT(_class="btn",_type="submit",_value=T("Submit")))
    form.append(INPUT(_class="btn btn-danger",_type="reset",_value=T("Reset")))

    if form.accepts(request,session,keepvalues=True):
        try:
            db(db.destinations.id==request.args[0]).update(destination=form.vars.destinationname, info = form.vars.info, isActive=form.vars.isActive, addedby=auth.user.id,addedat=datetime.datetime.now())
        except:
            response.flash =  sys.exc_info()[1]
        else:
            logger.info("Destination %s edited successfully by %s"%(form.vars.destinationname,auth.user.username))
            session.flash = T("Destination %(destination)s edited successfully",dict(destination=form.vars.destinationname))
            redirect(URL("index"))
    elif form.errors:
        response.flash = T('form has errors')

    return dict(form=form)
