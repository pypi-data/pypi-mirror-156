import datetime
import json
import os
import platform
import shlex
import socket
import subprocess
import time
from dataclasses import dataclass
from subprocess import TimeoutExpired
from typing import Any, Union

import plogger
from paramiko import SSHClient, ssh_exception, AutoAddPolicy


@dataclass
class ResponseParser:
    """Bash response parser"""

    response: Any

    @property
    def stdout(self) -> Union[str, dict]:
        return self.response[1]

    @property
    def stderr(self) -> str:
        return self.response[2]

    @property
    def exited(self) -> int:
        try:
            return int(self.response[0])
        except TypeError:
            return 0

    @property
    def ok(self) -> bool:
        return self.response[0] == 0

    @property
    def command(self) -> str:
        return self.response[3]

    @property
    def motd(self) -> str:
        """Get message of the day"""
        return self.response[4]

    def json(self):
        return json.loads(self.stdout)


class Plinux:
    """Base class to work with linux"""

    def __init__(self,
                 host: str = '127.0.0.1',
                 username: str = None,
                 password: str = None,
                 port: int = 22,
                 logger_enabled: bool = True):
        """Create a client object to work with linux host"""

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.logger = plogger.logger('Plinux', enabled=logger_enabled)

    def __str__(self):
        return f'Local host: {self.get_current_os_name()}\n' \
               f'Remote IP: {self.host}\n' \
               f'Username: {self.username}\n' \
               f'Password: {self.password}\n' \
               f'Host availability: {self.is_host_available()}\n' \
               f'Credentials are correct: {self.is_credentials_valid()}'

    def is_host_available(self, port: int = 0, timeout: int = 5):
        """Check remote host is available using specified port"""

        # return self._client().get_transport().is_active()
        port_ = port or self.port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((self.host, port_))
            return False if result else True

    def list_all_methods(self):
        """Returns all available public methods"""
        return [method for method in dir(self) if not method.startswith('_')]

    def run_cmd_local(self, cmd: str, timeout: int = 60):
        """Main function to send commands using subprocess

        :param cmd: string, command
        :param timeout: timeout for command
        :return: Decoded response

        """

        try:
            self.logger.info(f'COMMAND: "{cmd}"')
            cmd_divided = shlex.split(cmd)
            result = subprocess.run(cmd_divided, capture_output=True, timeout=timeout)

            out = result.stdout.decode().strip()
            err = result.stderr.decode().strip()
            response = result.returncode, out, err, cmd

            return ResponseParser(response)
        except subprocess.TimeoutExpired:
            self.logger.exception('Connection timeout')
            raise TimeoutExpired

    def run_cmd_local_native(self, *popenargs,
                             stdin_input=None,
                             capture_output: bool = False,
                             timeout: int = 60,
                             check: bool = False,
                             **kwargs):
        """It's just native subprocess' .run invocation.

        The returned instance will have attributes args, returncode, stdout and
        stderr. By default, stdout and stderr are not captured, and those attributes
        will be None. Pass stdout=PIPE and/or stderr=PIPE in order to capture them.

        If check is True and the exit code was non-zero, it raises a
        CalledProcessError. The CalledProcessError object will have the return code
        in the returncode attribute, and output & stderr attributes if those streams
        were captured.

        If timeout is given, and the process takes too long, a TimeoutExpired
        exception will be raised.

        There is an optional argument "stdin_input", allowing you to
        pass bytes or a string to the subprocess's stdin.  If you use this argument
        you may not also use the Popen constructor's "stdin" argument, as
        it will be used internally.

        By default, all communication is in bytes, and therefore any "stdin_input" should
        be bytes, and the stdout and stderr will be bytes. If in text mode, any
        "stdin_input" should be a string, and stdout and stderr will be strings decoded
        according to locale encoding, or by "encoding" if set. Text mode is
        triggered by setting any of text, encoding, errors or universal_newlines.

        The other arguments are the same as for the Popen constructor.

        :param popenargs:
        :param stdin_input:
        :param capture_output:
        :param timeout:
        :param check:
        :param kwargs:
        :return:
        """

        cmd = shlex.split(*popenargs)
        cmd_to_log = ' '.join(cmd)
        self.logger.info(f'COMMAND: "{cmd_to_log}"')

        result = subprocess.run(cmd, input=stdin_input, capture_output=capture_output, timeout=timeout,
                                check=check, **kwargs)

        return result

    def _client(self, sftp: bool = False, timeout: int = 15):
        """https://www.paramiko.org/"""

        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())

        try:
            client.connect(self.host, username=self.username, password=self.password, timeout=timeout)

            if sftp:
                return client.open_sftp()
            return client
        except ssh_exception.AuthenticationException as err:
            self.logger.exception('Authentication error')
            raise err
        except ssh_exception.NoValidConnectionsError as err:
            # Fixme add more sophisticated verification
            self.logger.exception('There is no valid connection. Try to use "_local" or vice versa method.')
            raise err
        except TimeoutError as err:
            self.logger.exception('Timeout exceeded.')
            raise err

    def run_cmd(self, cmd: str, sudo: bool = False, timeout: int = 30) -> ResponseParser:
        """Base method to execute SSH command on remote server

        :param cmd: SSH command
        :param sudo: Execute specified command as sudo user
        :param timeout: Execution timeout
        :return: ResponseParser class
        """

        client = self._client()

        try:
            command = f"sudo -S -p '' -- sh -c '{cmd}'" if sudo else cmd
            self.logger.info(f'[{self.host}] -> {command}')

            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)

            if sudo:
                stdin.write(self.password + '\n')
                stdin.flush()

            # Get exit code
            exited = stdout.channel.recv_exit_status()

            # Get STDOUT
            stdout = stdout.read().decode().strip()
            out = stdout if stdout else None
            self.logger.info(f'[{self.host}] <- {exited}: {out}')

            # Get STDERR
            stderr = stderr.read().decode().strip()

            # Clear stderr if password prompt detected
            if '[sudo] password for' in stderr:
                stderr = None

            err = stderr if stderr else None
            if err:
                self.logger.error(f'[{self.host}] <- {err}')

            response = exited, out, err, command
            return ResponseParser(response)
        finally:
            client.close()

    # noinspection PyTypeChecker
    def run_cmd_session(self, cmds: tuple = None, buffer_size: int = 4096) -> ResponseParser:
        """Send command using session. Returns entity name if noe command provided.

        :param cmds: List of commands to execute
        :param buffer_size: Bytes size to receive. Default 4096.
        :return:
        """

        client = self._client()

        with client.invoke_shell() as ssh:
            self.logger.info(f'[{self.host}] ' + ' -> '.join(cmds))

            ssh.settimeout(5)
            motd = ssh.recv(buffer_size).decode().strip()

            result = {}

            # Send command one-by-one
            for cmd in cmds:
                ssh.send(f'{cmd}\n')
                time.sleep(0.5)
                response = ssh.recv(buffer_size).decode().splitlines()
                result[cmd] = response[1:-1]

            response = None, result, result, cmds, motd
            return ResponseParser(response)

    @staticmethod
    def get_current_os_name():
        return platform.system()

    @property
    def __sudo_cmd(self):
        return f'sudo -S <<< {self.password}'

    def is_credentials_valid(self) -> bool:
        try:
            self.run_cmd('whoami')
            return True
        except ssh_exception.AuthenticationException:
            self.logger.exception(f'Invalid credentials ({self.username, self.password})')
            return False

    def get_os_version(self) -> dict:
        """Get OS version

        :return: {'distributor_id': 'Ubuntu', 'desc...': 'Ub..20.04.2 LTS', 'release': '20.04', 'codename': 'focal'}
        """

        result = self.run_cmd('lsb_release -a').stdout

        parsed_result = {}
        for line in result.splitlines():
            kev, value = line.split(':')
            new_key = kev.strip().lower().replace(' ', '_')
            parsed_result[new_key] = value.strip()

        return parsed_result

    def get_ip(self) -> str:
        """Get IP address of remote server"""

        return self.run_cmd('hostname -I').stdout

    def get_hostname(self) -> str:
        """Get hostname of remote server

        :return: Hostname. auto-test-node1
        """

        return self.run_cmd('hostname').stdout

    # Package, Deb
    def get_package_version(self, package: str) -> str:
        """Get package (.deb) version

        :param package: Deb name
        :return: 1.0.9.1503
        """

        cmd = f"dpkg -s {package} | grep Version | awk '{{print $2}}'"
        result = self.run_cmd(cmd)
        return result.stdout

    def get_installed_packages_versions(self) -> dict:
        """Get all installed packages and their versions"""

        response = self.run_cmd('dpkg --list | grep ii').stdout
        result = {package.split()[1].removesuffix(':amd64'): package.split()[2] for package in response.splitlines()}
        return result

    def is_package_upgradable(self, package: str, show_version: bool = True) -> Union[bool, str]:
        """Check package newer version. Return it if exists.

        :param show_version:
        :param package:
        :return:
        """

        cmd = fr"apt list --installed {package} 2>/dev/null | egrep -o '\[.*\]'"
        result = self.run_cmd(cmd).stdout

        try:
            if 'upgradable' in result:  # There is newer package version
                if show_version:  # Get precise version
                    new_version = result.split('to: ')[1].removesuffix(']')
                    return new_version
                return True
        except TypeError:
            self.logger.error(f'Package ({package}) not found on destination server.')
        return False

    def is_security_update_available(self) -> bool:
        """Verify security update availability. Returns True is available. Otherwise returns False"""

        result = self.run_cmd('apt-get upgrade -s | grep -i security')
        return result.ok

    def get_package_info(self, package: str) -> dict:
        """Get package info"""

        cmd = f'dpkg -s {package}'
        result = self.run_cmd(cmd).stdout
        res_dict = {}
        for line in result.splitlines():
            data = line.split(': ')
            key = data[0]
            value = data[1]

            if key == 'Depends':
                # [['starwind-san-and-nas-console', '(>= 1.1809.2586)'], ['starwind-virtual-san', '(>= 1.0.14398)']]
                depends_list = [x.split(' (', maxsplit=1) for x in value.split(', ')]
                depends_dict = {x[0]: x[1].removesuffix(')') for x in depends_list}
                res_dict[key] = depends_dict
            else:
                res_dict[key] = value

        return res_dict

    # FIXME
    def change_hostname(self, name: str):
        cmd = f'{self.__sudo_cmd} -- sh -c "echo {name} > /etc/hostname; hostname -F /etc/hostname"'
        self.run_cmd(cmd)
        cmd = f"""{self.__sudo_cmd} -- sh -c 
        'sed -i "/127.0.1.1.*/d" /etc/hosts; echo "127.0.1.1 {name}" >> /etc/hosts'"""
        return self.run_cmd(cmd)

    def get_date(self) -> datetime:
        """Get date from remote server"""

        result = self.run_cmd('date')
        return to_known_type(result.stdout)

    def get_time_date(self) -> dict:
        """Get time and date from remote server

        - time_sync_mode: service key with "ntp" or "host" value

        :return:
        """

        response = self.run_cmd('timedatectl').stdout.splitlines()

        response_dict = {}
        for line in response:
            key, value = line.strip().split(': ')
            key_new = key.replace(' ', '_').lower()

            if key_new == 'time_zone':
                value = value.split(' ')[0]
            response_dict[key_new] = to_known_type(value)

        response_dict['time_sync_mode'] = 'ntp' if response_dict['ntp_service'] == 'active' else 'host'

        return response_dict

    # ---------- Service management ----------
    def get_service(self, name: str):
        """Get whole service info"""

        return self.run_cmd(f'systemctl status {name}')

    def get_service_status(self, name: str):
        """Get service status"""

        return self.run_cmd(f'systemctl is-active {name}')

    def is_service_active(self, name: str) -> bool:
        cmd = f'systemctl is-active --quiet {name}'
        return self.run_cmd(cmd).ok

    def stop_service(self, name: str):
        return self.run_cmd(f'systemctl stop {name}', sudo=True)

    def kill_service(self, name: str):
        return self.run_cmd(f'systemctl kill {name}', sudo=True)

    def start_service(self, name: str):
        return self.run_cmd(f'systemctl start {name}', sudo=True)

    def restart_service(self, name: str):
        return self.run_cmd(f'systemctl restart {name}', sudo=True)

    def get_service_journal(self, name: str):
        return self.run_cmd(f'journalctl -u {name}', sudo=True)

    def list_active_services(self, no_legend: bool = True, all_services: bool = False):
        """
        List all active services and it's status

        :param no_legend:
        :param all_services: To see loaded but inactive units, too
        :return:
        """

        cmd = 'systemctl list-units -t service'
        if no_legend:
            cmd += ' --no-legend'
        if all_services:
            cmd += ' --all'
        return self.run_cmd(cmd)

    def enable(self, name: str):
        """Enable service using systemctl"""

        return self.run_cmd(f'systemctl enable {name}', sudo=True)

    def disable(self, name: str):
        """Disable service using systemctl"""

        return self.run_cmd(f'systemctl disable {name}', sudo=True)

    def is_enabled(self, name: str) -> bool:
        """Get unit service status

        :param name: Service name
        :return:
        """

        response = self.run_cmd(f'systemctl is-enabled {name}').stdout

        try:
            return True if 'enabled' in response else False
        except TypeError:
            return False

    def get_pid(self, name: str, sudo: bool = False) -> Union[int, list]:
        """Get process pid

        :param name: Process name
        :param sudo: To elevate permission (in CentOS)
        """

        result = self.run_cmd(f'pidof {name}', sudo=sudo).stdout

        try:
            return int(result)
        except ValueError:
            return list(map(int, result.split()))
        except TypeError as err:
            self.logger.exception(f'Cannot get pid ({name}). Try to use sudo.')
            raise err

    def get_netstat_info(self, params: str = ''):
        """Get netstat info

        Necessary to install net-tool: "yum -y install net-tools"

        :param params: "ltpu" - Active Internet connections (only servers)
        :return:
        """

        cmd_ = 'netstat' if not params else f'netstat -{params}'
        return self.run_cmd(cmd_)

    # ----------- File and directory management ----------
    def check_exists(self, path: str, sudo: bool = False) -> bool:
        r"""Check file and directory exists.

        For windows path: specify network path in row format or use escape symbol.
        You must be connected to the remote host.
        Usage: check_exists('\\\\172.16.0.25\\d$\\New Text Document.txt')

        For linux path: linux style path.
        Usage: check_exists('/home/user/test.txt')

        :param path: Full path to file/directory
        :param sudo:
        :return:
        """

        # Linux
        if '/' in path:
            cmd = f'test -e {path}'
            response = self.run_cmd(cmd, sudo=sudo)
            return response.ok
        # Windows
        elif '\\' in path:
            return os.path.exists(path)
        raise SyntaxError('Incorrect method usage. Check specified path.')

    def cat_file(self, path: str, sudo: bool = False) -> str:
        """Get file content"""

        result = self.run_cmd(f'cat {path}', sudo=sudo)
        return result.stdout

    def get_json(self, path: str, sudo: bool = False, pprint: bool = False, remove_bom: bool = False) -> dict:
        """Read JSON file as string and pretty print it into console

        :param path: Full file path
        :param sudo: Use sudo
        :param pprint: pretty print into console
        :param remove_bom: Remove Byte Order Mark
        :return:
        """

        file = self.cat_file(path, sudo=sudo)

        if remove_bom:
            file = file.encode().decode('utf-8-sig')

        jsoned = json.loads(file)

        if pprint:
            print(json.dumps(jsoned, indent=4), sep='')
        return jsoned

    def create_file(self, path: str, sudo: bool = True):
        return self.run_cmd(f'touch {path}', sudo=sudo)

    def clear_file(self, path: str, sudo: bool = True):
        """Clear file.

        :param path:
        :param sudo:
        :return:
        """

        return self.run_cmd(f'cat /dev/null > {path}', sudo=sudo)

    def get_file_permissions(self, path: str, human: bool = False, sudo: bool = False):
        """Display file or file system status.

        :param path: File path
        :param human: Access rights in human readable form otherwise in in octal
        :param sudo:
        :return:
        """

        cmd = f'stat -c %A {path}' if human else f'stat -c %a {path}'
        return self.run_cmd(cmd, sudo=sudo)

    def get_file_size(self, path: str, sudo: bool = False):
        """Get file size

        :param sudo:
        :param path: File path
        :return: size in bytes
        """

        return self.run_cmd(f'stat -c "%s" {path}', sudo=sudo)

    def grep_line_in_file(self, path: str, string: str, directory: bool = False, sudo: bool = True):
        """Grep line in file or directory

        :param sudo:
        :param path: File/directory path
        :param string: string pattern to grep
        :param directory: If True - grep in directory with files
        :return:
        """

        if directory:
            return self.run_cmd(f'grep -rn "{string}" {path}', sudo=sudo)
        return self.run_cmd(f'grep -n "{string}" {path}', sudo=sudo)

    def change_line_in_file(self, path: str, old: str, new: str, sudo: bool = True):
        """Replace line and save file.

        :param sudo:
        :param path: File path
        :param old: String to replace
        :param new: New string
        :return:
        """

        return self.run_cmd(f'sed -i "s!{old}!{new}!" {path}', sudo=sudo)

    def delete_line_from_file(self, path: str, string: str, sudo: bool = True):
        return self.run_cmd(f"sed -i '/{string}/d' {path}", sudo=sudo)

    def get_last_file(self, directory: str = '', name: str = '', sudo: bool = True) -> str:
        """Get last modified file in a directory

        :param sudo:
        :param name: Filename to grep
        :param directory: Directory path to precess. Home by default
        :return:
        """

        directory_ = directory or f'/home/{self.username}'
        cmd = f'ls {directory_} -Art| grep {name} | tail -n 1' if name else f'ls {directory} -Art | tail -n 1'
        return self.run_cmd(cmd, sudo=sudo).stdout

    def remove(self, path: str, sudo: bool = True):
        """Remove file(s) and directories

        Usage:\n
        path=/opt/1 remove the directory\n
        path=/opt/1/* remove all file in the directory\n
        path=/opt/1/file.txt remove specified file in the directory\n

        :param sudo:
        :param path: Path to a file or directory.
        """

        return self.run_cmd(f'for file in {path}; do rm -rf "$file"; done', sudo=sudo)

    def extract_files(self, src: str, dst: str, mode: str = 'tar', quite: bool = True, sudo: bool = False):
        """Extract file to specified directory

        :param sudo:
        :param src: Full path to archive (with extension)
        :param dst:
        :param mode: "tar", "zip"
        :param quite: Suppress list of unpacked files
        :return:
        """

        unzip_cmd = f'unzip -q {src} -d {dst}' if quite else f'unzip {src} -d {dst}'
        tar_cmd = f'tar -xzvf {src}.tar.gz -C {dst}'

        cmd = tar_cmd if mode == 'tar' else unzip_cmd

        return self.run_cmd(cmd, sudo=sudo)

    def copy_file(self, src: str, dst: str, sudo: bool = True):
        """Copy file to another location

        :param sudo:
        :param src: Source full path
        :param dst: Destination
        :return:
        """

        return self.run_cmd(f'cp {src} {dst}', sudo=sudo)

    def get_md5(self, path: str, sudo: bool = True) -> str:
        """Get file md5

        :param sudo:
        :param path: File path
        :return: Return md5 sum only
        """

        result = self.run_cmd(f'md5sum {path}', sudo=sudo).stdout
        return result.split(path)[0].strip()

    def get_processes(self) -> list:
        """Get processes using PS"""

        result = self.run_cmd('ps -aux')
        split_result = result.stdout.splitlines()
        return split_result

    #  ----------- Power management -----------
    def reboot(self):
        return self.run_cmd('shutdown -r now', sudo=True)

    def shutdown(self):
        return self.run_cmd('shutdown -h now', sudo=True)

    #  ----------- Directory management -----------
    def create_directory(self, path: str, sudo: bool = True):
        return self.run_cmd(f'mkdir {path}', sudo=sudo)

    def list_dir(self, path: str, params=None, sudo: bool = False) -> list:
        """List directory

        :param path: Directory path
        :param params: Additional params. For example: "la"
        :param sudo:
        :return: List of files
        """

        cmd = f'ls {path} -{params}' if params else f'ls {path}'
        result = self.run_cmd(cmd, sudo=sudo)

        try:
            return result.stdout.splitlines()
        except AttributeError:
            return []

    def count_files(self, path: str) -> int:
        """Count files number in directory.

        :param path:
        :return:
        """

        result = self.run_cmd(f'ls {path} | wc -l')
        return int(result.stdout)

    #  ----------- SFTP -----------
    @property
    def sftp(self):
        return self._client(sftp=True)

    def upload(self, local: str, remote: str):
        r"""Upload file/dir to the host and check exists after.

        Usage: tool.upload(r'd:\python_tutorial.pdf', '/home/user/python_tutorial.pdf'')

        :param local: Source full path
        :param remote: Destination full path
        :return: bool
        """

        self.sftp.put(local, remote, confirm=True)
        self.logger.info(f'Uploaded {local} to {remote}')
        return self.exists(remote)

    def download(self, remote: str, local: str, callback=None) -> bool:
        r"""Download a file from the current connection to the local filesystem and check exists after.

        Usage: tool.download('/home/user/python_tutorial.pdf', 'd:\dust\python_tutorial.pdf')

        :param remote: Remote file to download. May be absolute, or relative to the remote working directory.
        :param local: Local path to store downloaded file in, or a file-like object
        :param callback: func(int, int)). Accepts the bytes transferred so far and the total bytes to be transferred
        :return: bool
        """

        self.sftp.get(remote, local, callback=callback)
        self.logger.info(f'Downloaded {remote} to {local}')
        return self.exists(local)

    def change_password(self, new_password: str):
        """Change password

        BEWARE USING! You'll lost connection to a server after completion.

        echo username:new_password | sudo chpasswd

        :param new_password: New password with no complex check.
        :return:
        """

        return self.run_cmd(f'sudo -S <<< {self.password} -- sh -c "echo {self.username}:{new_password} | chpasswd"')

    # ---------- Disk ----------
    def get_disk_usage(self, mount_point: str = '/') -> dict:
        """Get disk usage

        :param mount_point:
        :return: {'Filesystem': '/dev/mapper/ubuntu--vg-ubuntu--lv', 'Size': '19G', 'Used': '12G', 'Avail': '6.5G',
        'Use%': '64%', 'Mounted': '/'}
        """

        cmd = f'df {mount_point} -h' if mount_point else 'df -h'
        result = self.run_cmd(cmd).stdout
        print(result.splitlines()[0].split())
        parsed_result = dict(zip(result.splitlines()[0].split(), result.splitlines()[1].split()))
        return parsed_result

    def get_free_space(self, mount_point: str = '/', *params) -> str:
        """Get free space.

        By default, with -h parameter.

        >>> self.get_free_space('')  # get all info
        >>> self.get_free_space('/opt')  # df / -h --output=avail | tail -n 1
        >>> self.get_free_space('/opt', '--block-size=K')  # df /opt --block-size=K --output=avail | tail -n 1
        >>> self.get_free_space('/opt', '-h', '-H')  # df /opt -h -H --output=avail | tail -n 1

        :param mount_point: /, /opt
        :return: 5G
        """

        params_ = shlex.join(params) if params else '-h'
        cmd = f'df {mount_point} {params_} --output=avail | tail -n 1'

        return self.run_cmd(cmd).stdout

    def get_disk_size(self, path: str, sudo: bool = False) -> int:
        """Get disk size.

        df /mnt/xfs/ --block-size=1 --output=size | tail -n 1

        :param path: /mnt/xfs/
        :param sudo:
        :return: Size in bytes
        """

        cmd = f'df {path} --block-size=1 --output=size | tail -n 1'
        result = self.run_cmd(cmd, sudo=sudo).stdout
        try:
            return int(result)
        except TypeError as err:
            self.logger.exception(f'Path ({path}) not found or something went wrong.')
            raise err

    def get_directory_size(self, path: str, sudo: bool = False) -> int:
        """Get directory size

        du --block-size=1 --total /mnt/ssd-cache/ | tail -n 1 | cut -f1

        :param path: /mnt/ssd-cache/
        :param sudo:
        :return: Size in bytes
        """

        cmd = f'du --block-size=1 --total {path} | tail -n 1 | cut -f1'
        result = self.run_cmd(cmd, sudo=sudo).stdout
        try:
            return int(result)
        except TypeError as err:
            self.logger.exception(f'Path ({path}) not found or something went wrong.')
            raise err

    def get_port_listeners_process_id(self, port: int) -> Union[int, list[int]]:
        r"""Get processes ids of port listeners

        sudo -S -p '' -- sh -c 'ss -ltpn | grep ":44301\s" | grep -Po "(?<=pid=)(\d*)" | uniq '

        :param port: /mnt/ssd-cache/
        :return: Size in bytes
        """

        cmd = fr'ss -ltpn | grep ":{port}\s" | grep -Po "(?<=pid=)(\d*)" | uniq'
        result = self.run_cmd(cmd, sudo=True).stdout
        try:
            return int(result)
        except TypeError as err:
            self.logger.exception(f'Path ({port}) not found or something went wrong.')
            raise err
        except ValueError:
            return list(map(int, result.splitlines()))

    def get_process_cmdline(self, *process_id: int, sudo: bool = False) -> list:
        """Get process command line

        ps h -p 507034,507033,507032,507031,507030,507029,507028,507027,507026 -o args

        :param process_id:
        :param sudo:
        :return: List of processes
        """

        ids = ','.join(map(str, process_id))  # convert to str comma separated
        cmd = f'ps h -p {ids} -o args'
        result = self.run_cmd(cmd, sudo=sudo).stdout

        return result.splitlines()

    def debug_info(self):
        """Show debug log. Logger must be enabled"""

        self.logger.info('Linux client created.')
        self.logger.info(f'Local host: {self.get_current_os_name()}')
        self.logger.info(f'Remote IP: {self.host}')
        self.logger.info(f'Username: {self.username}')
        self.logger.info(f'Password: {self.password}')
        self.logger.info(f'Available: {self.is_host_available()}')
        self.logger.info(f'Available: {self.is_host_available()}')

    # ---------- User management ----------
    def get_user_id(self, user: str = None) -> int:
        """Get Linux OS user ID

        :param user:
        :return: integer
        """

        user = self.username if user is None else user
        result = self.run_cmd(f'id -u {user}')
        return int(result.stdout)

    def kill_user_session(self, name: str):
        """
        Kill all user's ssh session and processes

        :param name: user name
        :return:
        """

        return self.run_cmd(f'pkill -9 -u {name}', sudo=True)

    def sqlite3(self, db: str, sql: str, sudo: bool = False, params: str = '', timeout: int = 1000):
        """Simple work with the SQLite. Can use ".json" in response.

        :param db: DB path
        :param sql: SQL request
        :param params: i.e. "-line -header", "-csv"
        :param sudo:
        :param timeout: ms. 1000 by default
        :return:
        """

        cmd = f'sqlite3 -cmd ".timeout {timeout}" {db} "{sql}" {params}'
        return self.run_cmd(cmd, sudo=sudo)

    # OpenSSL
    def validate_ssl_key(self, path: str) -> bool:
        """Validate key

        :param path: key path
        :return:
        """

        result = self.run_cmd(f'openssl rsa -in {path} -check')
        return True if 'RSA key ok' in result.stdout else False

    def get_ssl_md5(self, path: str):
        """Get cert or key md5

        :param path:
        :return:
        """

        return self.run_cmd(f'openssl x509 -noout -modulus -in {path} | openssl md5')

    def get_ssl_certificate(self, x509: bool = True, port: int = 443):
        """Get certificate info

        :param x509: Get x509 if specified
        :param port: 443 by default
        :return:
        """

        cmd = f'openssl s_client -showcerts -connect {self.host}:{port} </dev/null'
        if x509:
            cmd += ' | openssl x509 -text'
        return self.run_cmd(cmd)

    def get_ssl_fingerprint(self, path: str, algorithm: str = 'sha1', brief: bool = True) -> str:
        """Get SSL/TLS thumbprint

        :param path:
        :param algorithm:
        :param brief: Get fingerprint in "C3587D1515236324AB03686BF7F23B015D284351" format
        :return:
        """

        cmd_general = f'openssl x509 -noout -fingerprint -{algorithm} -inform pem -in {path}'
        if brief:
            cmd = f'{cmd_general} | awk -F "=" \'{{gsub(":","");print $2}}\''
        else:
            cmd = f'{cmd_general} | awk -F "=" \'{{print $2}}\''
        return self.run_cmd(cmd).stdout

    def get_ssl_serial(self, path: str) -> str:
        """Get serial number from certificate

        :param path:
        :return:
        """

        cmd_general = f'openssl x509 -noout -serial -inform pem -in {path}'  # | awk -F "=" \'{{print $2}}\''
        cmd = f'{cmd_general} | awk -F "=" \'{{print $2}}\''

        return self.run_cmd(cmd).stdout

    # NETWORK
    def get_ip_addresses_show(self, name: str = None) -> dict:
        """Show IP addresses info.

        - If name is specified, return only info about this interface.
        - If name is not specified, return all interfaces info.

        :param name: Interface name. Returns for specific iface info if used. For example: ens160, enp0s10f0
        :return:
        """

        cmd = 'ip --json addr show'
        result = self.run_cmd(cmd).json()

        result_dict = {iface['ifname']: iface for iface in result}

        for key, value in result_dict.items():
            # Set IP address as keys in addr_info dict
            addr_info_dict = {addr['local']: addr for addr in value['addr_info']}
            result_dict[key]['addr_info'] = addr_info_dict
            result_dict[key]['ipv4_addresses'] = [k for k, v in addr_info_dict.items() if v['family'] == 'inet']
            result_dict[key]['ipv6_addresses'] = [k for k, v in addr_info_dict.items() if v['family'] == 'inet6']

        result_dict['entities_quantity'] = len(result)

        return result_dict if name is None else result_dict[name]

    def get_ntp_servers(self) -> set:
        """Get NTP servers list

        :return: Set of NTP servers. {'172.16.0.1', '192.168.12.1'}
        """

        cmd = 'grep "NTP" /etc/systemd/timesyncd.conf | grep -v "#"'
        response = self.run_cmd(cmd).stdout
        try:
            result = response.removeprefix('NTP=')
        except AttributeError:
            return set()
        return set(result.split())

    # Aliases
    ps = get_processes
    ls = list_dir
    cp = copy_file
    date = get_date
    os = get_os_version
    exists = check_exists
    netstat = get_netstat_info
    start = start_service
    stop = stop_service
    status = get_service_status
    restart = restart_service
    version = get_os_version
    rm = remove
    chpasswd = change_password
    count = count_files
    stat = get_file_permissions
    md5 = get_md5


def to_known_type(value: str):
    """Convert string data into known Python's data types.

    - date/time => datetime.datetime
    - "yes"/"no"/"true"/"false" => True/False
    - "none", "empty", ""  => True/False
    - "123"  => int
    - "000000"  => "000000"

    :param value:
    :return:
    """

    from dateutil import parser
    from dateutil.parser import ParserError

    try:
        value_lower = value.lower()
    except AttributeError:
        value_lower = value

    try:
        return int(value_lower)
    except (TypeError, ValueError):
        ...

    if value_lower in ('yes', 'true'):
        return True
    elif value_lower in ('no', 'false'):
        return False
    elif value_lower in ('none', 'empty', ''):
        return None
    elif value_lower.startswith('00'):
        return value

    try:
        return parser.parse(value)
    except ParserError:
        ...

    return value
