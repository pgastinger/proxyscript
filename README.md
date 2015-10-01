# proxyscript

## Why
We are running a shared proxy cluster with approx. 30000 users and 20 different customers. Each customer has it's own requirements (customer related exceptions) and therefore it's own proxy script (PAC-file). These files used to be static files served by an Apache web server cluster. For new entries or changes, vi was used to edit these files directly on the webserver. This method was rather error-prone, hard to manage and tracking changes was difficult. As an alternative, this interface was built. It is not necessary to have SSH-access to the productive web server, multiple changes can be made easily and no more vi typos.

## Description
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

### Quick Start
- define destination
- define customer
- add entries (mapping destination - customer)
- check with PAC-File tester / take a look at the generated file
- copy PAC-File to server

## Screenshots
* Overview of active customers
![image](https://cloud.githubusercontent.com/assets/3997488/10218881/aaf2290a-683a-11e5-8ade-b854ebcb16de.png)
* PAC-File Tester
![image](https://cloud.githubusercontent.com/assets/3997488/10218962/4bdc2672-683b-11e5-97a9-31b86ce3fe5c.png)

## Support
I may not have time for support, but if you are interested or if you have questions, just send me an email. (peter.gastinger@gmail.com)

