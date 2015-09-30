# proxyscript

This web2py-interface is a rather simple gui for creating customer specific proxy pac files. The interface runs on any recent Linux-distribution (Python 2.7 preferred) and is basically just a generator, which runs on my raspberry pi. 
After generating the proxy script, it can be copied to a redundant LAMP-webserver where it will be fetched by the actual proxy clients. 
Following components are used for that:
* web2py (http://www.web2py.com/)
* IPy (https://pypi.python.org/pypi/IPy/, included as module)
* Datatables-Plugin for jquery (https://www.datatables.net/, included)
* pacparser (https://github.com/pacparser/pacparser, must be manually compiled and installed)

By default, a sqlite-database is used (which can easily changed to either MySQL, ...). Authentication is local only, but this can also easily changed to a LDAP authentication against a Microsoft Active Directory. 

## Demo
A demo with sample data is running at:
* url: https://proxyscripts.secitec.net
* user: jdemo
* password: proxyscript

## Screenshots
![image](https://cloud.githubusercontent.com/assets/3997488/10199865/5199ff5a-67a3-11e5-8fb2-ce5fd6b93df7.png)

