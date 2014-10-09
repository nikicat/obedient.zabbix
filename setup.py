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
        package_data={'obedient.zabbix': [
            'zabbix_server.conf',
            'apache.conf',
            'zabbix.conf.php',
            'frontend.sh',
            'zabbix.sh',
        ]},
        entry_points={'obedient': [
            'create = obedient.zabbix:create',
        ]},
        install_requires=[
            'dominator[full] >=11.6',
        ],
    )
