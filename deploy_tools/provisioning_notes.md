Provisioning a new site
=======================

## Required packages:
 * nginx
 * Python 3
 * Git
 * pip
 * virtualenv

 eg, on Ubuntu:

  sudo apt-get install nginx git python3 python3-pip
  sudo pip3 install virtualenv

## Nginx Virtual Host config

* see nginx.template.confi
* replace SITENAME with, eg, staging.my.domain.com

## Upstart Job

* see gunicorn-upstart.template.conf
* replace SITENAME with, eg, staging.my.domain.com

## Systemd Service

* see gunicorn-systemd.template.service
* replace SITENAME with, eg, staging.my.domain.com

## Folder structure:
    /home/username
    `-- superlist-staging.sandbox.dev
        |-- database
        |-- source
        |-- static
        `-- virtualenv
