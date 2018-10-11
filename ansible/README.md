### Introduction

This Ansible Role will install GeoNode and required dependencies onto an Ubuntu
14.04 (Trusty) host. It includes tasks for PostgreSQL+PostGIS, GeoServer, GeoNode,
 nginx, uswgi and also includes tasks for using AWS RDS databases. It is meant
 to be used with a GeoNode template project by following the workflow
 described here http://github.com/geonode/geonode-project

Tested with a known minimal working Ansible version of 1.9.3.

### Installing roles from ansible galaxy

The ansible playbook that performs the provisioning depends on a few roles provided in the
ansible galaxy.  You can install these rolls with the following command in this directory:

```
ansible-galaxy install -r requirements.yml
```

### Role Variables

* `app_name` - GeoNode project name (default: `geonode`)
* `github_user` - GitHub username that owns the project (default: `GeoNode`)
* `code_repository` - URL to the Code Repository (default: `https://github.com/{{ github_user }}/{{ app_name }}.git`)

The `app_name` variable will be used to set the database names and credentials. You can override this behavior with the following variables.

* `db_data_instance` - Database instance for spatial data (default: `{{ app_name }}`)
* `db_metadata_instance` - Database instance for the application metadata (default: `{{ app_name }}_app`)
* `db_password` - Database password (default: `{{ app_name }}`)
* `db_user` - Database user (default: `{{ app_name }}`)

You can also change the war used to deploy geoserver with the following variable.

* `geoserver_url` - GeoServer war URL (default: `http://build.geonode.org/geoserver/latest/geoserver.war`)

### Dataqs Processors

* roles/dataqs/templates/dataq_settings.py:
    * Change the 'DATAQS_APPS' setting to add/remove individual dataqs processors
    * Change the 'CELERYBEAT_SCHEDULE' setting to add/remove/modify scheduled dataqs celery tasks

### Setting up a vagrant box

To configure a local development virtual machine, you will need to have virtualbox and vagrant installed.
Note: You may need to change the IP configuration in the VagrantFile to a valid ip on the local network

    $ vagrant up geoservices
    $ vagrant ssh geoservices


Note: You may need to bring the vagrant box down and up for geonode to work.

    $ vagrant halt
    $ vagrant up


## Deploying to ec2 (or other server)

Several variables have to be set correctly before deploying to a remote server. This can be achived by creating a custom inventory with the group ```[geoservices]``` and the host you will deploy too.

```
[geoservices]
XXX.XXX.XXX.XXX ansible_ssh_private_key_file=PATH_TO_PEM_FILE ansible_user=ubuntu deploy_user=ubuntu site_url=http://ec2-XXX-XXX-XXX-XXX.us-west-2.compute.amazonaws.com/ server_name=XXX-XXX-XXX-XXX-XXX.us-west-2.compute.amazonaws.com
```

Replace X's with the IP address of the remote server

* `ansible_user` - will be the user ansible SSHes in as
* `deploy_user` - will be the user used to deploy and install all the software (usually the same as ansible_user)
* `ansible_ssh_private_key_file` - the PEM file that corresponds to the ansible_user and provides passwordless ssh access
* `site_url` - the url of the website - used by geonode to identify its base URL
* `server_name` - the fully qualified domain name of the server

To deploy, run ```ansible-playbook -i /path/to/inventory playbook.yml``` From this directory.

Alternately,  variables may be placed in a local variables file,  e.g.:

/path/to/local_vars.yml
```yaml
ansible_ssh_private_key_file: PATH_TO_PEM_FILE
ansible_user: ubuntu
deploy_user: ubuntu
site_url: http://ec2-XXX-XXX-XXX-XXX.us-west-2.compute.amazonaws.com/
server_name: ec2-XXX-XXX-XXX-XXX.us-west-2.compute.amazonaws.com
```

With an inventory:

/path/to/inventory
```
[geoservices]
XXX.XXX.XXX.XXX
```

To deploy,  run:

```
ansible-playbook -i /path/to/inventory -e @/path/to/local_vars.yml playbook.yml
```
