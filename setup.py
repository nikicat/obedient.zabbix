import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='obedient.zabbix',
        version='0.1.0',
        url='https://github.com/yandex-sysmon/obedient.zabbix',
        license='LGPLv3',
        author='Nikolay Bryskin',
        author_email='devel.niks@gmail.com',
        description='Zabbix obedient for Dominator',
        platforms='linux',
        packages=['obedient.zabbix'],
        namespace_packages=['obedient'],
        package_data={'obedient.zabbix': ['zabbix_server.conf']},
        entry_points={'obedient': [
            'local = obedient.zabbix:make_local',
            'one-host = obedient.zabbix:make_for_host',
        ]},
        install_requires=[
            'dominator[full] >=11.1',
        ],
    )
