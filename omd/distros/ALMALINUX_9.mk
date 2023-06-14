DISTRO_CODE       = el9
OS_PACKAGES       =
OS_PACKAGES      += libcap # needed for setting special file permissions
OS_PACKAGES      += time # needed for mk-job
OS_PACKAGES      += traceroute # needed for Checkmk parent scan
OS_PACKAGES      += curl
OS_PACKAGES      += dialog
OS_PACKAGES      += expat
OS_PACKAGES      += graphviz
OS_PACKAGES      += graphviz-gd
OS_PACKAGES      += httpd
OS_PACKAGES      += libevent
OS_PACKAGES      += libtool-ltdl
OS_PACKAGES      += logrotate
OS_PACKAGES      += rpcbind
OS_PACKAGES      += pango
OS_PACKAGES      += perl-Locale-Maketext-Simple
OS_PACKAGES      += perl-IO-Zlib
OS_PACKAGES      += perl-Net-Ping
OS_PACKAGES      += perl-lib
OS_PACKAGES      += php
OS_PACKAGES      += php-cli
OS_PACKAGES      += php-xml
OS_PACKAGES      += php-mbstring
OS_PACKAGES      += php-pdo
OS_PACKAGES      += php-gd
OS_PACKAGES      += php-json
OS_PACKAGES      += readline
OS_PACKAGES      += rsync
OS_PACKAGES      += uuid
OS_PACKAGES      += cronie
OS_PACKAGES      += freeradius-utils
OS_PACKAGES      += libpcap # needed for ICMP of CMC
OS_PACKAGES      += glib2 # needed by msitools/Agent Bakery
OS_PACKAGES      += bind-utils # needed for check_dns
OS_PACKAGES      += poppler-utils # needed for preview of PDF in reporting
OS_PACKAGES      += libgsf # needed by msitools/Agent Bakery
OS_PACKAGES      += cpio # needed for Agent bakery (solaris pkgs)
OS_PACKAGES      += binutils # Needed by Checkmk Agent Bakery
OS_PACKAGES      += rpm-build # Needed by Checkmk Agent Bakery
#OS_PACKAGES      += pyOpenSSL # needed for Agent Bakery (deployment)
OS_PACKAGES       += libffi # needed for pyOpenSSL and dependant
OS_PACKAGES       += openldap-compat # needed for ldap
OS_PACKAGES       += procps # needed for having pgrep available
OS_PACKAGES      += libpq
OS_PACKAGES      += mod_auth_mellon # for this distro, we're not shipping it and using the system packages
USERADD_OPTIONS   = -M
ADD_USER_TO_GROUP = gpasswd -a %(user)s %(group)s
PACKAGE_INSTALL   = yum -y makecache ; yum -y install
ACTIVATE_INITSCRIPT = chkconfig --add %s && chkconfig %s on
APACHE_CONF_DIR   = /etc/httpd/conf.d
APACHE_INIT_NAME  = httpd
APACHE_USER       = apache
APACHE_GROUP      = apache
APACHE_VERSION    = 2.4.6
APACHE_CTL        = /usr/sbin/apachectl
APACHE_MODULE_DIR = /usr/lib/httpd/modules
APACHE_MODULE_DIR_64 = /usr/lib64/httpd/modules
HTPASSWD_BIN      = /usr/bin/htpasswd
PHP_FCGI_BIN      = /usr/bin/php-cgi
APACHE_ENMOD      = true %s
BECOME_ROOT       = su -c
MOUNT_OPTIONS     =
INIT_CMD          = /usr/bin/systemctl %(action)s %(name)s.service
