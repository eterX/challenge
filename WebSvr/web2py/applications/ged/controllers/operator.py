# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
import os
from subprocess import check_output

@auth.requires_membership('Operator')
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Operator's Interface")
    response.title = "Operator's Interface"
    formpath = FORM("Specify new path: ",
                INPUT(_name='path', requires=IS_NOT_EMPTY(),value=session.current_path), INPUT(_type='submit'))
    if formpath.accepts(request,session):

        print("path accepted: {}".format(formpath.vars.path))
        session.current_path=formpath.vars.path
#        process = os.popen('source /opt/ros/kinetic/setup.bash; rosrun ged ged_client.py {current_path}'.format(current_path=session.current_path))
 #       process.close()


        output = check_output("""
            source /opt/ros/kinetic/setup.bash
            rosrun ged ged_client.py "{current_path}"

            """.format(current_path=session.current_path),
            shell=True, executable='/bin/bash')
        print(output.decode())
        response.flash = 'path executed'

    elif formpath.errors:
        response.flash = 'path has errors'


    formabort = FORM("Click to abort: ",INPUT(_type='submit', value="current mission"))
    if formabort.accepts(request,session):
        print("abort mission: {}".format(formabort.vars.path))
        output = check_output("""
            source /opt/ros/kinetic/setup.bash
            rostopic pub -1 /ged/ged_server_py/cancel actionlib_msgs/GoalID "stamp: secs: 0 nsecs: 0 id: ''"
            """.format(current_path=session.current_path),
            shell=True, executable='/bin/bash')
        print(output.decode())
        response.flash = 'mission aborted'



    #"[[8.0,8.0,0.0],[8.0,3.0,0.0],[3.0,8.0,0.0],[3.0,3.0,0.0]]"

    return dict(message=T('Welcome to web2py!'),formpath=formpath,current_path=session.current_path, formabort=formabort  )




def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


