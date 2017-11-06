#!/bin/bash

exec > >(tee -a /usr/local/osmosix/logs/service.log) 2>&1
echo "Executing service script.."

# RUN EVERYTHING AS ROOT
if [ "$(id -u)" != "0" ]; then
    exec sudo "$0" "$@"
fi

OSSVC_HOME=/usr/local/osmosix/service

. /usr/local/osmosix/etc/.osmosix.sh
. /usr/local/osmosix/etc/userenv
. $OSSVC_HOME/utils/cfgutil.sh
. $OSSVC_HOME/utils/nosqlutil.sh
. $OSSVC_HOME/utils/install_util.sh
. $OSSVC_HOME/utils/os_info_util.sh
. $OSSVC_HOME/utils/agent_util.sh

export ANSIBLE_DIR=/home/ansible-playbooks
export dir_name=ansible-playbooks


root_dir="$( cd "$( dirname $0 )" && pwd )"
echo Root dir $root_dir

setupprereqs() {
 agentSendLogMessage "Installing PreReqs.."
  yum -y install wget unzip
  yum -y install epel-release
  yum -y install ansible

  mkdir -p $ANSIBLE_DIR
  cd $ANSIBLE_DIR
  agentSendLogMessage "AnsibleDir: $ANSIBLE_DIR"
  agentSendLogMessage "Playbook URL: $playbookzip"
  wget $playbookzip
  unzip playbooks.zip
}

runplaybook() {
  agentSendLogMessage "Deploying playbook.."

 cd $ANSIBLE_DIR/playbooks
 echo "localhost ansible_connection=local" >> /etc/ansible/hosts
 ansible-playbook main.yml

}

setupprereqs
runplaybook
