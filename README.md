# plh414_2017_2018_directoryservicepython
plh414 2017/2018 Directory Service Sample Python



Προσθέτουμε στο αρχείο /etc/apache2/sites-available/000-default.conf πριν το κλείσιμο του </Virtualhost> το παρακάτω και εκτελούμε μετά
service apache2 restart

```
WSGIDaemonProcess directoryservicepython user=www-data group=www-data processes=1 threads=5
WSGIScriptAlias /directoryservicepython /var/www/directoryservicepython/app.wsgi
<Directory /var/www/directoryservicepython>
    WSGIProcessGroup directoryservicepython
    WSGIApplicationGroup %{GLOBAL}
    Require all granted
</Directory>
```

It is important to use only 1 process in the WSGIDaemonProcess directive, as each process this process is used to create the ephemeral node for zookeeper for this fileservice.

To use more processes to handle more concurrent requests (and use multiple CPUs), the processes must somehow make sure that only one ephemeral node is created.


Possible deploy script
```
#!/bin/bash
if [ "$#" -ne 7 ]; then
    echo "Illegal number of parameters"
    echo "deploy.sh ZOOKEEPER_HOST ZOOKEEPER_USERNAME ZOOKEEPER_PASSWORD  SERVERHOSTNAME SERVER_PORT SERVER_SCHEME CONTEXT"
    echo "e.g. ../deploy.sh  snf-814985.vm.okeanos.grnet.gr username password snf-814985.vm.okeanos.grnet.gr 80 http directoryservicepython"
    exit -1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ZOOKEEPER_HOST=$1 >> "$DIR/config.properties"
echo ZOOKEEPER_USER=$2 >> "$DIR/config.properties"
echo ZOOKEEPER_PASSWORD=$3 >> "$DIR/config.properties"
echo SERVERHOSTNAME=$4 >> "$DIR/config.properties"
echo SERVER_PORT=$5 >> "$DIR/config.properties"
echo SERVER_SCHEME=$6 >> "$DIR/config.properties"
echo CONTEXT=$7 >> "$DIR/config.properties"


# after deploying, reload apache. Then call status url to get available FS
cd $DIR \
&& rsync -a -v --exclude deploy.sh --exclude .git --exclude data --delete $DIR/ root@$4:/var/www/directoryservicepython \
&& ssh root@$4 "chown -R www-data:www-data /var/www/directoryservicepython && service apache2 reload && wget $6://$4:$5/$7/status -O -"
cd $DIR

# ./deploy.sh snf-814985.vm.okeanos.grnet.gr username password snf-814985.vm.okeanos.grnet.gr 80 http directoryservicepython

```
