#!/bin/bash
DOCKER_SVCNAME=tomcat7
OSSVC_HOME=/usr/local/osmosix/service
SVCHOME="$OSSVC_HOME/$DOCKER_SVCNAME"

. $OSSVC_HOME/utils/docker_util.sh
. $OSSVC_HOME/utils/nosqlutil.sh
. $OSSVC_HOME/utils/cfgutil.sh

DOCKER_IMAGE_NAME=`getDockerImageName $DOCKER_SVCNAME`

installTomcatDocker(){
    loadDockerImage $DOCKER_IMAGE_NAME
}

generateTomcatDockerConfig(){
log "[TOMCAT CONFIGURATION] - Generating tomcat config file"
    # Note
    # Only if the app server is top tier, we would enable https and https rederct, otherwise certificates install, encryption and redirects are taken care at the top tier and we just open port 80 here.
    SERVER_XML="/usr/local/$DOCKER_SVCNAME/conf/server.xml"
    WEB_XML="/usr/local/$DOCKER_SVCNAME/conf/web.xml"

    mkdir -p "/usr/local/$DOCKER_SVCNAME/conf"

    cp $SVCHOME/conf/* /usr/local/$DOCKER_SVCNAME/conf

    if [ "$topTier" != "true" ]; then
        replaceToken $SERVER_XML "%UN_PRIV_HTTP_PORT%" 80
        uncommentXml $SERVER_XML "CUSTOM_HTTP_PORT_ENABLED"
    else

        if [ "$cliqrInternalHttpEnabled" == 1 ]; then
            uncommentXml $SERVER_XML "INTERNAL_HTTP_ENABLED"
        fi

        if [ "$cliqrExternalHttpEnabled" == 1 ]; then
            replaceToken $SERVER_XML "%UN_PRIV_HTTP_PORT%" 80
            uncommentXml $SERVER_XML "CUSTOM_HTTP_PORT_ENABLED"
        fi

        if [ "$cliqrExternalHttpsEnabled" == 1 ]; then
            if [ -r "$cliqrSSLCert" -a -f "$cliqrSSLCert" -a -r "$cliqrSSLKey"  -a -f "$cliqrSSLKey" ];
            then
                SSL_DIR=$OSMOSIX_INSTALL_DIR/$DOCKER_SVCNAME/conf/ssl
                mkdir -p $SSL_DIR
                cp $cliqrSSLCert $SSL_DIR/cliqrSSLCert
                cp $cliqrSSLKey $SSL_DIR/cliqrSSLKey
                replaceToken $SERVER_XML "%UN_PRIV_HTTPS_PORT%" 443
                uncommentXml $SERVER_XML "CUSTOM_HTTPS_PORT_ENABLED"
                replaceToken $SERVER_XML "%SSL_CERT%" $SSL_DIR/cliqrSSLCert
                replaceToken $SERVER_XML "%SSL_KEY%" $SSL_DIR/cliqrSSLKey
            else
                log "[LISTERNING PORT] - Listening on HTTPS port but certificates are missing"
                log "HTTPS is enabled but certificates are missing or unreadable"
            fi
        fi

            if [ "$cliqrForceHttpRedirect" == 1 ]; then
                    uncommentXml $WEB_XML "FORCE_HTTP_REDIRECT"
                    log "[REDIRECTION] Forcing HTTPS redirect"
            fi
    fi

    log "[CONFIGURATION] Configuring DB settings"
    cd /usr/local/$DOCKER_SVCNAME/webapps/$cliqrWebappContext
    overrideNosqlIp
    BACKUP_DIR=$SVCHOME/bkp/
    CFG_LIST=(`echo $cliqrWebappConfigFiles | tr ";" "\n"`)
    for cfgFile in "${CFG_LIST[@]}"
    do
        echo "[RESTORE CONFIG FILE] $cfgFile"
        cp "$BACKUP_DIR/$cfgFile" $cfgFile
        replaceToken $cfgFile "%NOSQLDB_TIER_IP%" $CliqrTier_NoSQLDatabase_IP
        replaceToken $cfgFile "%DB_TIER_IP%" $CliqrTier_Database_IP
        replaceToken $cfgFile "%MB_TIER_IP%" $CliqrTier_MsgBus_IP
        replaceToken $cfgFile "%BC_TIER_IP%" $CliqrTier_BackendCache_IP
        replaceTierIpToken $cfgFile
    done
    log "[CONFIGURATION] Configured DB settings"

    log "[TOMCAT CONFIGURATION] - Successfully generated tomcat config file"

}
startTomcatDockerService(){
    removeDockerContainer $DOCKER_SVCNAME
    docker run -d -v /usr/local/$DOCKER_SVCNAME/conf:/usr/local/tomcat/conf -v /usr/local/$DOCKER_SVCNAME/webapps:/usr/local/tomcat/webapps -p 80:80 -p 443:443 --name=$DOCKER_SVCNAME $DOCKER_IMAGE_NAME
}
stopTomcatDockerService(){
    docker stop $DOCKER_SVCNAME
    docker rm -f $DOCKER_SVCNAME
}
restartTomcatDockerService(){
    stopTomcatDockerService
    startTomcatDockerService
}


