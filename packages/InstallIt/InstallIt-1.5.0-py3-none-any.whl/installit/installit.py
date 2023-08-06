'''Bright Edge eServices installation utilities

Utilities for installing a Linux machine.
'''
import logging
from pathlib import Path
import shutil
from termcolor import colored
from beetools import beearchiver, beeutils, beescript, beevenv

_PROJ_DESC = __doc__.split("\n")[0]
_PROJ_PATH = Path(__file__)
_PROJ_NAME = _PROJ_PATH.stem


class InstallIt:
    '''Bright Edge eServices server installation tools

    Parameters
    ----------

    Returns
    -------

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent

    '''

    webconfig_file_name: Path
    reahlmailutil_cnf_file_name: Path

    def __init__(self, p_parent_logger_name=None):
        '''Initialize the class
        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        self.success = True
        if p_parent_logger_name:
            self.logger_name = '{}.{}'.format(p_parent_logger_name, _PROJ_NAME)
            self.logger = logging.getLogger(self.logger_name)
        self.curr_os = beeutils.get_os()
        self.mysql_linux_cfg_pth = Path(
            '/', 'etc', 'mysql', 'mysql.conf.d', 'mysqld.cnf'
        )
        self.mysql_linux_app_pth = Path('mysql')
        self.mysql_win_cfg_pth = Path(
            'C:\\', 'ProgramData', 'MySQL', 'MySQL Server 8.0', 'my.ini'
        )
        self.mysql_win_app_pth = Path(
            'C:\\', 'Program Files', 'MySQL', 'MySQL Server 8.0', 'bin', 'mysql.exe'
        )
        self.reahlmailutil_cnf_file_name = Path('mailutil.config.py')
        self.reahl_cnf_file_name = Path('reahl.config.py')
        self.systemaccountmodel_cnf_file_name = Path('systemaccountmodel.config.py')
        self.webconfig_file_name = Path('web.config.py')

    def append_to_nfs_cnf(self, p_share_list, p_verbose=False):
        '''Amend the nfs configuration file
        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''

        if self.curr_os == beeutils.LINUX:
            nfs_config_pth = Path('/', 'etc', 'exports')
            contents = nfs_config_pth.read_text()
            for share in p_share_list:
                contents += '{}\n'.format('\t\t'.join(share))
            nfs_config_pth.write_text(contents)
            if p_verbose:
                print(colored('{}\n{}'.format(nfs_config_pth, contents), 'yellow'))
        pass

    def create_linux_users(self, p_new_users, p_verbose=False):
        '''Create new linux users
        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        rc = 0
        success = True
        if self.curr_os == beeutils.LINUX:
            import crypt

            c_user_name = 0
            c_passwd = 1
            p_sudo = 2
            for user in p_new_users:
                cmd = [
                    'sudo',
                    'useradd',
                    '-p',
                    crypt.crypt(user[c_passwd], crypt.METHOD_SHA256),
                    '-m',
                    user[c_user_name],
                ]
                rc = beescript.exec_cmd(cmd)
                if len(user) == 3:
                    if user[p_sudo].lower() == 'sudo':
                        cmd = ['sudo', 'usermod', '-aG', 'sudo', user[c_user_name]]
                        rc = beescript.exec_cmd(cmd, p_verbose=p_verbose)
            if rc != 0:
                success = False
        return success

    def create_mysql_users(self, p_admin_user, p_new_users, p_verbose=False):
        '''Create a new mysql user

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        rc = 0
        c_user_name = 0
        c_passwd = 1
        c_host = 2
        cmd_base = self.make_sql_base_cmd(p_admin_user)
        for user in p_new_users:
            cmd = cmd_base.copy()
            cmd.append(
                '''CREATE USER '{}'@'{}' IDENTIFIED BY '{}';'''.format(
                    user[c_user_name], user[c_host], user[c_passwd]
                )
            )
            rc = beescript.exec_cmd(cmd, p_verbose=p_verbose)
        cmd = cmd_base + ['''FLUSH PRIVILEGES;''']
        rc = beescript.exec_cmd(cmd, p_verbose=p_verbose) and rc
        return rc

    def create_nginx_config(
        self,
        p_domain_name,
        p_folder,
        p_reahl_app_name,
        p_site_active=True,
        p_verbose=False,
    ):
        '''Create nginx configuration file

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        file_name = '{}.conf'.format(p_domain_name)
        if p_verbose:
            print(colored('Create {} - {}'.format(p_domain_name, file_name), 'yellow'))
        sites_avail_dir = Path(p_folder, 'sites-available')
        sites_avail_dir.mkdir(parents=True, exist_ok=True)
        sites_enabled_dir = Path(p_folder, 'sites-enabled')
        sites_enabled_dir.mkdir(parents=True, exist_ok=True)
        nginx_app_available_pth = sites_avail_dir / '{}.conf'.format(p_domain_name)
        nginx_app_enabled_pth = sites_enabled_dir / '{}.conf'.format(p_domain_name)
        file_contents = [
            'server {',
            '\tlisten 80;',
            '\tserver_name {0} www.{0};'.format(p_domain_name),
            '\taccess_log /var/log/nginx/{}.access.log combined;'.format(p_domain_name),
            '\terror_log /var/log/nginx/{}.error.log;'.format(p_domain_name),
            '',
            '\tlocation / {',
            '\t\tinclude uwsgi_params;',
            '\t\tuwsgi_param HTTPS off;',
            '\t\tuwsgi_pass unix:///var/run/uwsgi/app/{}/socket;'.format(
                p_reahl_app_name
            ),
            '\t\tuwsgi_ignore_headers     Set-Cookie;',
            '\t}',
            '}',
        ]
        beescript.write_script(nginx_app_available_pth, file_contents)
        if p_site_active:
            if self.curr_os == beeutils.LINUX:
                if nginx_app_enabled_pth.is_symlink():
                    nginx_app_enabled_pth.unlink()
                nginx_app_enabled_pth.symlink_to(nginx_app_available_pth)
            else:
                if nginx_app_enabled_pth.is_file():
                    nginx_app_enabled_pth.unlink()
                shutil.copy(nginx_app_available_pth, nginx_app_enabled_pth)
        pass

    def create_reahl_config(
        self,
        p_reahl_app_name,
        p_folder,
        p_db_dir,
        p_db_system,
        p_db_userid,
        p_db_pwd,
        p_verbose=False,
    ):
        '''Create Reahl configuration file

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        if p_verbose:
            print(
                colored(
                    'Create {} - {}'.format(p_reahl_app_name, self.reahl_cnf_file_name),
                    'yellow',
                )
            )
        path = Path(p_folder, p_reahl_app_name)
        path.mkdir(parents=True, exist_ok=True)
        path = path / self.reahl_cnf_file_name
        file_contents = ["reahlsystem.root_egg = '{}'".format(p_reahl_app_name)]
        if p_db_system in ['mysql', 'postgresql']:
            file_contents.append(
                "reahlsystem.connection_uri = '{}://{}:{}@localhost/{}'".format(
                    p_db_system, p_db_userid, p_db_pwd, p_reahl_app_name
                )
            )
        elif p_db_system == 'sqlite':
            file_contents.append(
                "reahlsystem.connection_uri = '{}:///{}/{}.db'".format(
                    p_db_system, p_db_dir, p_reahl_app_name
                )
            )
        file_contents.append('reahlsystem.debug = False')
        beescript.write_script(path, file_contents)
        pass

    def create_reahl_mailutil_config(
        self, p_reahl_app_name, p_folder, p_settings, p_verbose=False
    ):
        '''Create Reahl MailUtil configuration file.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        if p_verbose:
            print(
                colored(
                    'Create {} - {}'.format(
                        p_reahl_app_name, self.reahlmailutil_cnf_file_name
                    ),
                    'yellow',
                )
            )
        path = Path(p_folder, p_reahl_app_name)
        path.mkdir(parents=True, exist_ok=True)
        path = path / self.reahlmailutil_cnf_file_name
        beescript.write_script(path, p_settings)
        pass

    def create_reahl_systemaccountmodel_config(
        self, p_reahl_app_name, p_folder, p_admin_email, p_verbose=False
    ):
        '''Create Reahl SystemAccountModel config file.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        if p_verbose:
            print(
                colored(
                    'Create {} - {}'.format(
                        p_reahl_app_name, self.systemaccountmodel_cnf_file_name
                    ),
                    'yellow',
                )
            )
        path = Path(p_folder, p_reahl_app_name)
        path.mkdir(parents=True, exist_ok=True)
        path = path / self.systemaccountmodel_cnf_file_name
        file_contents = ["accounts.admin_email = '{}'".format(p_admin_email)]
        beescript.write_script(path, file_contents)
        pass

    def create_reahl_web_config(
        self,
        p_reahl_app_name,
        p_folder,
        p_www_dir,
        p_website_root='MainPageUI',
        p_verbose=False,
    ):
        '''Create a Reahl Web  configuration file.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        if p_verbose:
            print(
                colored(
                    'Create {} - {}'.format(p_reahl_app_name, self.webconfig_file_name),
                    'yellow',
                )
            )
        path = Path(p_folder, p_reahl_app_name)
        path.mkdir(parents=True, exist_ok=True)
        path = path / self.webconfig_file_name
        www_pth = p_www_dir / p_reahl_app_name
        www_pth.mkdir(parents=True, exist_ok=True)
        file_contents = [
            'from {} import {}'.format(p_reahl_app_name, p_website_root),
            'web.site_root = {}'.format(p_website_root),
            'web.default_http_port = 80',
            'web.encrypted_http_port = 443',
            "web.static_root = '{}'".format(www_pth),
        ]
        beescript.write_script(path, file_contents)
        pass

    def create_uwsgi_ini(
        self,
        p_reahl_app_name,
        p_folder,
        p_parms,
        p_venv_base_dir,
        p_venv_name,
        p_verbose=False,
    ):
        '''Create uwsgi ini file

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        reahl_app_name = self.get_reahl_app_name(p_reahl_app_name)
        file_name = '{}.ini'.format(reahl_app_name)
        if p_verbose:
            print(
                colored('Create {} - {}'.format(p_reahl_app_name, file_name), 'yellow')
            )
        apps_available_dir = p_folder / 'apps-available'
        apps_available_dir.mkdir(parents=True, exist_ok=True)
        apps_enabled_dir = p_folder / 'apps-enabled'
        apps_enabled_dir.mkdir(parents=True, exist_ok=True)
        uwsgi_app_available_pth = apps_available_dir / file_name
        uwsgi_app_enabled_pth = apps_enabled_dir / file_name
        file_contents = [
            '[uwsgi]',
            'plugins = python3',
            'virtualenv = {}'.format(beevenv.get_dir(p_venv_base_dir, p_venv_name)),
            'module = {}wsgi'.format(reahl_app_name),
            'enable-threads = true',
            'processes = {}'.format(p_parms['uwsgiProcesses']),
            'threads = {}'.format(p_parms['uwsgiThreats']),
            'lazy = true',
            'harakiri = 20',
        ]
        beescript.write_script(uwsgi_app_available_pth, file_contents)
        if p_parms['AppActive']:
            if self.curr_os == beeutils.LINUX:
                if uwsgi_app_enabled_pth.is_symlink():
                    uwsgi_app_enabled_pth.unlink()
                uwsgi_app_enabled_pth.symlink_to(uwsgi_app_available_pth)
            else:
                if uwsgi_app_enabled_pth.is_file():
                    uwsgi_app_enabled_pth.unlink()
                shutil.copy(uwsgi_app_available_pth, uwsgi_app_enabled_pth.parent)
        pass

    def configure_mysql_remote_access(
        self, p_admin_user, p_new_users, p_user_rights, p_verbose=False
    ):
        '''Configure MySql remote access.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''

        def change_config_file(p_mysql_cnf_pth):
            success = True
            file_contents = b''
            found = False
            with p_mysql_cnf_pth.open(encoding='utf-8') as mysql_ptr:
                for line in mysql_ptr.readlines():
                    if line.find('bind-address') >= 0 and not found:
                        bind_address_list = line.split('=')
                        line = line.replace(bind_address_list[1], ' 0.0.0.0')
                        found = True
                    file_contents += bytes('{}\n'.format(line.strip()), 'utf-8')
                if not found:
                    file_contents += b'\n# Listen to the following connections\nbind-address\t\t= 0.0.0.0\n'
            mysql_ptr.close()
            rc = p_mysql_cnf_pth.write_bytes(file_contents)
            if rc < 0:
                success = False
            return success

        # end change_config_file

        success = True
        if self.curr_os == beeutils.LINUX:
            mysql_cnf_pth = self.mysql_linux_cfg_pth
        else:
            mysql_cnf_pth = self.mysql_win_cfg_pth
            pass
        if self.curr_os == beeutils.LINUX:
            if beescript.exec_cmd(['sudo', 'chmod', '666', mysql_cnf_pth]) < 0:
                success = False
        success = change_config_file(mysql_cnf_pth) and success
        success = (
            self.create_mysql_users(p_admin_user, p_new_users, p_verbose) and success
        )
        success = (
            self.grant_mysql_user_rights(p_admin_user, p_user_rights, p_verbose)
            and success
        )
        if self.curr_os == beeutils.LINUX:
            if beescript.exec_cmd(['sudo', 'systemctl', 'restart', 'mysql']) < 0:
                success = False
        return success

    def delete_linux_users(self, p_del_users, p_report_err=True, p_verbose=False):
        '''Delete a linux user

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        rc = 0
        if self.curr_os == beeutils.LINUX:
            c_user_name = 0
            # c_passwd = 1
            for user in p_del_users:
                cmd = ['sudo', 'userdel', '-r', '-f', user[c_user_name]]
                rc = beescript.exec_cmd(cmd, p_verbose=p_verbose)
        return rc

    def delete_mysql_users(
        self, p_admin_user, p_del_users, p_report_err=True, p_verbose=False
    ):
        '''Delete mysql users

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        rc = 0
        c_user_name = 0
        c_host = 1
        cmd_base = self.make_sql_base_cmd(p_admin_user)
        for user in p_del_users:
            cmd = cmd_base.copy()
            cmd.append(
                '''DROP USER '{}'@'{}';'''.format(user[c_user_name], user[c_host])
            )
            rc = beescript.exec_cmd(cmd, p_verbose=p_verbose)
        return rc

    @staticmethod
    def get_reahl_app_name(p_reahl_app_wheel_name):
        '''Get reahl app name

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        reahl_app_name = p_reahl_app_wheel_name.split('-')[0]
        return reahl_app_name

    def grant_mysql_user_rights(self, p_admin_user, p_user_rights, p_verbose=False):
        '''Grant mysql user rights

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        c_user_name = 0
        # c_passwd = 1
        c_host = 1
        c_db = 2
        c_table = 3
        c_grant = 4
        c_rights = 5
        rc = 0
        cmd_base = self.make_sql_base_cmd(p_admin_user)
        for right in p_user_rights:
            grant_rights = ''
            if right[c_grant] == 'Y':
                grant_rights = ' WITH GRANT OPTION'
            cmd = cmd_base + [
                '''GRANT {} ON {}.{} TO '{}'@'{}'{};'''.format(
                    ','.join(right[c_rights:]),
                    right[c_db],
                    right[c_table],
                    right[c_user_name],
                    right[c_host],
                    grant_rights,
                )
            ]
            rc = beescript.exec_cmd(cmd, p_verbose=p_verbose)
        cmd = cmd_base + ['''FLUSH PRIVILEGES;''']
        rc = beescript.exec_cmd(cmd, p_verbose=p_verbose) and rc
        return rc

    def make_sql_base_cmd(self, p_user=[False, False]):
        '''Make mysql base command for the os

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        c_user_name = 0
        c_passwd = 1
        if self.curr_os == beeutils.WINDOWS:
            cmd_base = [
                '{}'.format(self.mysql_win_app_pth),
                '--defaults-file={}'.format(str(self.mysql_win_cfg_pth)),
            ]
        else:
            cmd_base = ['sudo', self.mysql_linux_app_pth]
        if p_user[c_user_name]:
            cmd_base.append('--user={}'.format(p_user[c_user_name]))
        if p_user[c_passwd]:
            cmd_base.append('--password={}'.format(p_user[c_passwd]))
        cmd_base.append('-e')
        return cmd_base

    @staticmethod
    def make_userid(p_reahl_app_name):
        '''Make a user id conforming to the BEE naming conventions

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        user_name = '{}User'.format(p_reahl_app_name).lower()
        return user_name

    @staticmethod
    def make_user_passwd(p_reahl_app_name):
        '''Make a user id with the defined cypher

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        mid_sec = p_reahl_app_name[1:-1]
        cypher = {
            'a': '@',
            'e': '3',
            'i': '1',
            'o': '0',
            'u': '^',
            'c': '(',
            's': '$',
            't': '+',
            'z': '2',
        }
        for key in cypher:
            mid_sec = mid_sec.lower().replace(key, cypher[key])
        password = '{}{}{}'.format(
            p_reahl_app_name[0].upper(), mid_sec, p_reahl_app_name[-1]
        )
        return password

    def start_fire_wall(self):
        '''Start the fire wall on Linux

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        # No proper doctest (<<<) because it is os dependent

        '''
        if self.curr_os == beeutils.LINUX:
            switches = ['-x']
            script_name = 'start_fire_wall'
            script_cmds = ['yes | sudo ufw enable', 'sudo ufw status']
            beescript.exec_batch_in_session(
                script_cmds,
                p_script_name=script_name,
                p_verbose=True,
                p_switches=switches,
            )
        pass


def do_examples(p_cls=True):
    '''Examples to show implementation

    Parameters
    ----------
    p_cls
        Clear teh screen at start-up (True)

    Returns
    -------
    bool
        Correct execution (True | False)

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent

    '''

    def basic_test():
        '''Basic test'''

        def read_file(p_pth):
            data = []
            with (open(p_pth, "r")) as file_ptr:
                raw_data = file_ptr.readlines()
            for line in raw_data:
                data.append(line.strip('\n'))
            return data

        # end read_file

        def clean_up(p_folder):
            folders_to_remove = [
                Path(p_folder, 'nginx'),
                Path(p_folder, 'nginx'),
                Path(p_folder, 'RealtimeeventsCo'),
                Path(p_folder, 'RealTimeEventsWS'),
                Path(p_folder, 'test'),
                Path(p_folder, 'TestVenv_Env'),
                Path(p_folder, 'uwsgi'),
                Path(p_folder, 'www'),
            ]
            for folder in folders_to_remove:
                beeutils.rm_tree(folder)
                print(colored('Remove {}'.format(folder), 'yellow'))
            pass

        # end clean_up

        success = True
        data_test_dir = venv_base_dir = b_tls.app_root_dir / 'Data'
        www_dir = data_test_dir / 'www'
        admin_email = 'admin@realtimeevents.co'
        app_name = 'RealTimeEventsWS'
        db_dir = data_test_dir / 'reahl' / 'db'
        db_user_name = 'Testing01'
        db_pwd = '1re$UtseT'
        domain_name = 'realtimeevents.co'
        linux_users = [['Testing01', '1re$UtseT', 'sudo'], ['Testing02', '2re$UtseT']]
        mysql_admin_user = ['root', 'En0l@Gay']
        new_mysql_users = [
            ['Testing01', '1re$UtseT', 'localhost'],
            ['Testing02', '2re$UtseT', 'localhost'],
        ]
        new_mysql_remote_users = [['t_rtremote', 't_rtremote', '%']]
        nginx_config_file_name = 'realtimeevents.co.conf'
        reahl_cnf_file_name = 'reahl.config.py'
        reahlmailutil_cnf_file_name = 'mailutil.config.py'
        reahl_web_config_file_name = 'web.config.py'
        systemaccountmodel_cnf_file_name = 'systemaccountmodel.config.py'
        t_nginx_config = [
            'server {',
            '\tlisten 80;',
            '\tserver_name realtimeevents.co www.realtimeevents.co;',
            '\taccess_log /var/log/nginx/realtimeevents.co.access.log combined;',
            '\terror_log /var/log/nginx/realtimeevents.co.error.log;',
            '',
            '\tlocation / {',
            '\t\tinclude uwsgi_params;',
            '\t\tuwsgi_param HTTPS off;',
            '\t\tuwsgi_pass unix:///var/run/uwsgi/app/RealTimeEventsWS/socket;',
            '\t\tuwsgi_ignore_headers     Set-Cookie;',
            '\t}',
            '}',
        ]
        t_reahl_config_settings = [
            "reahlsystem.root_egg = 'RealTimeEventsWS'",
            "reahlsystem.connection_uri = 'mysql://Testing01:1re$UtseT@localhost/RealTimeEventsWS'",
            'reahlsystem.debug = False',
        ]
        t_reahl_mail_util_config_settings = ['mail.smtp_port = 25']
        t_reahl_web_config_contents = [
            'from RealTimeEventsWS import HomePageUI',
            'web.site_root = HomePageUI',
            'web.default_http_port = 80',
            'web.encrypted_http_port = 443',
            "web.static_root = '{}'".format(www_dir / 'RealTimeEventsWS'),
        ]
        t_system_account_model_contents = [
            "accounts.admin_email = 'admin@realtimeevents.co'"
        ]
        uwsgi_parms = {'uwsgiProcesses': 2, 'uwsgiThreats': 2, 'AppActive': True}
        user_rights = [
            ['root', 'localhost', '*', '*', 'Y', 'ALL'],
            ['Testing01', 'localhost', '*', '*', 'Y', 'ALL'],
            ['Testing02', 'localhost', '*', '*', 'N', 'SELECT', 'INSERT'],
        ]
        remote_user_rights = [
            [
                new_mysql_remote_users[0][0],
                new_mysql_remote_users[0][2],
                '*',
                '*',
                'N',
                'ALL',
            ]
        ]
        venv_name = 'TestVenv'
        uwsgi_ini_file_name = '{}.ini'.format(app_name)
        web_site_root = 'HomePageUI'
        del_mysql_users = [[x[0], x[2]] for x in new_mysql_users]
        del_my_remote_users = [[x[0], x[2]] for x in new_mysql_remote_users]
        if not data_test_dir.is_dir():
            data_test_dir.mkdir()
        t_install_utils = InstallIt()
        t_uwsgi_ini_contents = [
            '[uwsgi]',
            'plugins = python3',
            'virtualenv = {}'.format(venv_base_dir / '{}_env'.format(venv_name)),
            'module = RealTimeEventsWSWsgi',
            'enable-threads = true',
            'processes = 2',
            'threads = 2',
            'lazy = true',
            'harakiri = 20',
        ]
        if t_install_utils.curr_os == beeutils.LINUX:
            beescript.exec_cmd(
                ['sudo', 'chmod', '-R', 'u+wrx,g+wrx,o+wrx', data_test_dir]
            )
        clean_up(data_test_dir)
        t_install_utils.create_reahl_mailutil_config(
            app_name, data_test_dir, t_reahl_mail_util_config_settings, p_verbose=True
        )
        if (
            read_file(Path(data_test_dir, app_name, reahlmailutil_cnf_file_name))
            != t_reahl_mail_util_config_settings
        ):
            success = success and False
            beeutils.result_rep(success, 'create_reahl_mailutil_config')
        t_install_utils.create_reahl_config(
            app_name,
            data_test_dir,
            db_dir,
            'mysql',
            db_user_name,
            db_pwd,
            p_verbose=True,
        )
        if (
            read_file(Path(data_test_dir, app_name, reahl_cnf_file_name))
            != t_reahl_config_settings
        ):
            success = success and False
            beeutils.result_rep(success, 'create_reahl_config')
        t_install_utils.create_reahl_systemaccountmodel_config(
            app_name, data_test_dir, admin_email, p_verbose=True
        )
        if (
            read_file(Path(data_test_dir, app_name, systemaccountmodel_cnf_file_name))
            != t_system_account_model_contents
        ):
            success = success and False
            beeutils.result_rep(success, 'create_reahl_systemaccountmodel_config')
        t_install_utils.create_reahl_web_config(
            app_name, data_test_dir, www_dir, web_site_root, p_verbose=True
        )
        if (
            read_file(Path(data_test_dir, app_name, reahl_web_config_file_name))
            != t_reahl_web_config_contents
        ):
            success = success and False
            beeutils.result_rep(success, 'create_reahl_web_config')
        t_install_utils.create_uwsgi_ini(
            app_name,
            Path(data_test_dir, 'uwsgi'),
            uwsgi_parms,
            venv_base_dir,
            venv_name,
            p_verbose=True,
        )
        if (
            read_file(
                Path(data_test_dir, 'uwsgi', 'apps-available', uwsgi_ini_file_name)
            )
            != t_uwsgi_ini_contents
            and read_file(
                Path(data_test_dir, 'uwsgi', 'apps-enabled', uwsgi_ini_file_name)
            )
            != t_uwsgi_ini_contents
        ):
            success = success and False
            beeutils.result_rep(success, 'create_uwsgi_ini')
        t_install_utils.create_nginx_config(
            domain_name,
            Path(data_test_dir, 'nginx'),
            app_name,
            uwsgi_parms['AppActive'],
            p_verbose=True,
        )
        if (
            read_file(
                Path(data_test_dir, 'nginx', 'sites-available', nginx_config_file_name)
            )
            != t_nginx_config
            and read_file(
                Path(data_test_dir, 'nginx', 'sites-enabled', nginx_config_file_name)
            )
            != t_nginx_config
        ):
            success = success and False
            beeutils.result_rep(success, 'create_nginx_config')
        if not t_install_utils.delete_linux_users(
            linux_users, p_report_err=False, p_verbose=True
        ):
            success = success and False
            beeutils.result_rep(success, 'delete_linux_users')
        if not t_install_utils.create_linux_users(linux_users, p_verbose=True):
            success = success and False
            beeutils.result_rep(success, 'create_linux_users')
        if not t_install_utils.delete_linux_users(linux_users, p_verbose=True):
            success = success and False
            beeutils.result_rep(success, 'delete_linux_users')
        if not t_install_utils.delete_mysql_users(
            mysql_admin_user, del_mysql_users, p_report_err=False, p_verbose=True
        ):
            success = success and False
            beeutils.result_rep(success, 'delete_mysql_users')
        if not t_install_utils.create_mysql_users(
            mysql_admin_user, new_mysql_users, p_verbose=True
        ):
            success = success and False
            beeutils.result_rep(success, 'create_mysql_users')
        if not t_install_utils.grant_mysql_user_rights(
            mysql_admin_user, user_rights, p_verbose=True
        ):
            success = success and False
            beeutils.result_rep(success, 'create_mysql_users')
        if not t_install_utils.delete_mysql_users(
            mysql_admin_user, del_mysql_users, p_report_err=False, p_verbose=True
        ):
            success = success and False
            beeutils.result_rep(success, 'delete_mysql_users')
        if not t_install_utils.delete_mysql_users(
            mysql_admin_user, del_my_remote_users, p_report_err=False, p_verbose=True
        ):
            success = success and False
            beeutils.result_rep(success, 'delete_mysql_users')
        if t_install_utils.curr_os == beeutils.LINUX:
            if not t_install_utils.configure_mysql_remote_access(
                mysql_admin_user,
                new_mysql_remote_users,
                remote_user_rights,
                p_verbose=True,
            ):
                success = success and False
                beeutils.result_rep(success, 'configure_mysql_remote_access')
        if not t_install_utils.delete_mysql_users(
            mysql_admin_user, del_my_remote_users, p_report_err=False, p_verbose=True
        ):
            success = success and False
            beeutils.result_rep(success, 'delete_mysql_users')
        return success

    success = True
    b_tls = beearchiver.Archiver(_PROJ_DESC, _PROJ_PATH)
    # logger = logging.getLogger(_name)
    # logger.setLevel(beetools.DEF_LOG_LEV)
    # file_handle = logging.FileHandler(beetools.LOG_FILE_NAME, mode='w')
    # file_handle.setLevel(beetools.DEF_LOG_LEV_FILE)
    # console_handle = logging.StreamHandler()
    # console_handle.setLevel(beetools.DEF_LOG_LEV_CON)
    # file_format = logging.Formatter(
    #     beetools.LOG_FILE_FORMAT, datefmt=beetools.LOG_DATE_FORMAT
    # )
    # console_format = logging.Formatter(beetools.LOG_CONSOLE_FORMAT)
    # file_handle.setFormatter(file_format)
    # console_handle.setFormatter(console_format)
    # logger.addHandler(file_handle)
    # logger.addHandler(console_handle)

    b_tls.print_header(p_cls)
    print(
        beearchiver.msg_milestone(
            '==[ Start Testing InstallIt ]==========================================='
        )
    )
    success = basic_test()
    beeutils.result_rep(success, 'Completed')
    print(
        beearchiver.msg_milestone(
            '--[ End testing InstallIt ]------------------------------------'
        )
    )
    b_tls.print_footer()
    return success


def project_desc():
    return _PROJ_DESC


if __name__ == '__main__':
    do_examples()
