#!/usr/bin/env python

from __future__ import print_function

import os
import datetime
import subprocess
import tarfile
import ConfigParser


TOOL_ROOT = '/home/user/backups/'
BACKUPS_ROOT = os.path.join(TOOL_ROOT, 'data')
WWW_BACKUPS_ROOT = os.path.join(BACKUPS_ROOT, 'www')
DB_BACKUPS_ROOT = os.path.join(BACKUPS_ROOT, 'database')

WEB_ROOT = '/var/www/vhosts/'

config = os.path.join(TOOL_ROOT, 'conf', 'wp_backup.ini')

parser = ConfigParser.ConfigParser()

if len(parser.read(config)) == 0:
    raise Exception('ERROR: No config file {} found!'.format(config))


def www_backup(source_dir, output_file):

    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

    #print ("\nBackup content: ")
    #with tarfile.open(output_file, 'r') as tar:
    #    for data in tar.getmembers():
    #        print(data.name)

for section in parser.sections():

    print('Executing WWW data backup on: {}'.format(section))

    today = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')
    source_dir = parser.get(section, 'www_data').strip("\'")
    backup_name = os.path.join(WWW_BACKUPS_ROOT, section + '-' + today + '.gz')

    www_backup(source_dir, backup_name)

    print('\nExecuting MySQL data backup on: {}\n'.format(section))
    mysql_host = parser.get(section, 'mysql_host')
    mysql_db = parser.get(section, 'mysql_db')
    mysql_user = parser.get(section, 'mysql_user')
    mysql_pass = parser.get(section, 'mysql_pass')

    mysql_backup_file = os.path.join(DB_BACKUPS_ROOT, parser.get(section, 'mysql_db') + '-' + today + '.sql')

    print ('Using: HOST: {}\nDB: {}\nUSER: {}\n'.format(mysql_host, mysql_db, mysql_user, mysql_pass))

    dump_cmd = ['mysqldump ' +
                '--user={mysql_user} '.format(mysql_user=mysql_user) +
                '--password={db_pw} '.format(db_pw=mysql_pass) +
                '--host={db_host} '.format(db_host=mysql_host) +
                '{db_name} '.format(db_name=mysql_db) +
                '> ' +
                '{filepath}'.format(filepath=mysql_backup_file)]
    dump = subprocess.Popen(dump_cmd, shell=True)
    dump.wait()
