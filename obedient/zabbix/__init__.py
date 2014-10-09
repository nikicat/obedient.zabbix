from textwrap import dedent
from dominator.utils import resource_string, cached
from dominator.entities import (SourceImage, Image, DataVolume, ConfigVolume, TemplateFile,
                                Container, LogVolume, Url,
                                Shipment, Door, TextFile, LogFile, Task)


@cached
def make_zabbix_image():
    return SourceImage(
        name='zabbix',
        parent=Image(namespace='yandex', repository='trusty'),
        scripts=[
            'wget http://repo.zabbix.com/zabbix/2.4/ubuntu/pool/main/z/\
zabbix-release/zabbix-release_2.4-1+trusty_all.deb',
            'dpkg -i zabbix-release_2.4-1+trusty_all.deb',
            'apt-get update',
        ],
        entrypoint=['bash'],
    )


@cached
def make_server_image():
    return SourceImage(
        name='zabbix-server',
        parent=make_zabbix_image(),
        ports={'zabbix-trapper': 10051},
        scripts=[
            'DEBIAN_FRONTEND=noninteractive apt-get install -y zabbix-server-pgsql '
            'strace snmp-mibs-downloader fping nmap',
        ],
        files={
            '/scripts/zabbix.sh': resource_string('zabbix.sh'),
        },
        volumes={
            'logs': '/var/log/zabbix',
            'config': '/etc/zabbix'
        },
        command=['/scripts/zabbix.sh'],
    )


def make():
    frontend_image = SourceImage(
        name='zabbix-frontend',
        parent=make_zabbix_image(),
        scripts=[
            'apt-get install -y zabbix-frontend-php apache2 php5-pgsql',
            'chmod go+rx /etc/zabbix',
        ],
        files={
            '/scripts/frontend.sh': resource_string('frontend.sh'),
        },
        command=['/scripts/frontend.sh'],
    )

    postgres_image = SourceImage(
        name='postgres',
        parent=Image(repository='postgres', namespace=None, registry=None),
    )

    postgres = Container(
        name='postgres',
        image=postgres_image,
        doors={'postgres': Door(port=5432, schema='postgres')},
        volumes={
            'logs': LogVolume(dest='/var/log/postgresql'),
            'data': DataVolume(dest='/var/lib/postgresql/data'),
            # 'config': ConfigVolume(dest='/etc/postgresql'),
        },
    )

    backend = Container(
        name='zabbix-backend',
        image=make_server_image(),
        doors={'zabbix-trapper': Door(schema='zabbix-trapper')},
        privileged=True,  # needed for strace to work
        volumes={
            'logs': LogVolume(
                dest='/var/log/zabbix',
                files={
                    'zabbix_server.log': LogFile()
                },
            ),
            'config': ConfigVolume(
                dest='/etc/zabbix',
                files={'zabbix_server.conf': TemplateFile(
                    resource_string('zabbix_server.conf'),
                    postgres=postgres,
                )},
            ),
        },
    )

    frontend = Container(
        name='zabbix-frontend',
        image=frontend_image,
        privileged=True,  # needed to chmod /etc/zabbix
        doors={
            'http': Door(
                schema='http',
                urls={'default': Url('zabbix')},
            ),
        },
        volumes={
            'logs': LogVolume(
                dest='/var/log/apache2',
                files={
                    'access.log': LogFile(),
                    'error.log': LogFile(),
                },
            ),
            'config-apache': ConfigVolume(
                dest='/etc/zabbix',
                files={
                    'apache.conf': TextFile(resource_string('apache.conf')),
                    'web/zabbix.conf.php': TemplateFile(
                        resource_string('zabbix.conf.php'),
                        postgres=postgres,
                        backend=backend,
                    ),
                },
            ),
        },
    )

    def make_reinit_script():
        return TextFile(dedent('''#!/bin/bash
            cmd='psql -U postgres -h {door.host} -p {door.port}'
            echo 'drop database zabbix; create database zabbix;' | $cmd
            cd /usr/share/zabbix-server-pgsql
            cat schema.sql images.sql data.sql | $cmd zabbix
            '''.format(door=postgres.doors['postgres'])))
    reinit = make_db_task('reinit', make_reinit_script)

    def make_dump_script():
        return TextFile('pg_dump -U postgres -h {door.host} -p {door.port} -c -C '
                        'zabbix'.format(door=postgres.doors['postgres']))
    dump = make_db_task('dump', make_dump_script)

    def make_restore_script():
        return TextFile('psql -U postgres -h {door.host} -p {door.port}'.format(door=postgres.doors['postgres']))
    restore = make_db_task('restore', make_restore_script)

    return [postgres, frontend, backend], [reinit, dump, restore]


def make_db_task(name, script):
    return Task(
        name=name,
        image=make_server_image(),
        volumes={
            'scripts': ConfigVolume(
                dest='/scripts',
                files={'run.sh': script}
            ),
        },
        command=['/scripts/run.sh'],
    )


def create(ships):
    allcontainers = []
    alltasks = []
    for ship in ships:
        containers, tasks = make()
        for cont in containers:
            ship.place(cont)
        ship.containers['zabbix-backend'].doors['zabbix-trapper'].expose(10051)
        ship.containers['zabbix-frontend'].doors['http'].expose(80)
        ship.expose_all(range(15000, 16000))

        allcontainers.extend(containers)
        alltasks.extend(alltasks)
    return Shipment(name='', containers=allcontainers, tasks=alltasks)
