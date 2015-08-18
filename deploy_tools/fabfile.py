from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, sudo
import random

REPO_URL = 'https://github.com/ythuang/superlist.git'


def _create_directory_structure_if_necessary(site_folder):
    folder_list = {'database', 'static', 'virtualenv', 'source'}
    for subfolder in folder_list:
        run('mkdir -p %s/%s' % (site_folder, subfolder))


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, source_folder))
    current_commit = local('git log -n 1 --format=%H')
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/superlists/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["%s"]' % (site_name,)
        )
    secret_key_file = source_folder + '/superlists/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/requirements.txt' % (virtualenv_folder, source_folder))


def _update_static_files(source_folder):
    run('cd %s && ../virtualenv/bin/python3 manage.py collectstatic --noinput' % (source_folder,))


def _update_database(source_folder):
    run('cd %s && ../virtualenv/bin/python3 manage.py migrate --noinput' % (source_folder,))


def _setup_nginx(source_folder, username, sitename):
    tmp_config = '%s/deploy_tools/%s' % (source_folder, sitename)
    nginx_config = '/etc/nginx/sites-available/%s' % (sitename,)
    active_nginx_config = '/etc/nginx/sites-enabled/%s' % (sitename,)
    if exists(nginx_config):
        sudo('rm %s' % (nginx_config,))
        sudo('rm %s' % (active_nginx_config,))

    run('cp %s/deploy_tools/nginx.template.conf %s' % (source_folder, tmp_config))
    sed(tmp_config, "SITENAME", sitename)
    sed(tmp_config, "USERNAME", username)
    sudo('mv %s %s' % (tmp_config, nginx_config))
    sudo('ln -s %s %s' % (nginx_config, active_nginx_config))


def _setup_gunicorn_systemd(source_folder, username, sitename):
    tmp_config = '%s/deploy_tools/gunicorn-%s.service' % (source_folder, sitename)
    gunicorn_config = '/lib/systemd/system/gunicorn-%s.service' % (sitename,)
    if exists(gunicorn_config):
        sudo('rm %s' % (gunicorn_config,))

    run('cp %s/deploy_tools/gunicorn-systemd.template.service %s' % (source_folder, tmp_config))
    sed(tmp_config, "SITENAME", sitename)
    sed(tmp_config, "USERNAME", username)
    sudo('mv %s %s' % (tmp_config, gunicorn_config))


def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)
    _setup_nginx(source_folder, env.user, env.host)
    _setup_gunicorn_systemd(source_folder, env.user, env.host)
