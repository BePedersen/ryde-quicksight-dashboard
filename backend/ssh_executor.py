import paramiko
import io

class SSHExecutor:
    def __init__(self, hostname, username="pi", key_filename=None):
        self.hostname = hostname
        self.username = username
        self.key_filename = key_filename
        self.client = None

    def connect(self):
        """Connect to Pi via SSH"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.key_filename:
                self.client.connect(
                    self.hostname,
                    username=self.username,
                    key_filename=self.key_filename,
                    timeout=5
                )
            else:
                # Try default key locations
                self.client.connect(
                    self.hostname,
                    username=self.username,
                    timeout=5
                )
            return True
        except Exception as e:
            print(f"SSH connection failed to {self.hostname}: {e}")
            return False

    def execute(self, command):
        """Execute command and return output"""
        try:
            if not self.client:
                self.connect()

            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')

            return {
                "success": True,
                "output": output,
                "error": error
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }

    def read_env(self):
        """Read .env file from Pi"""
        result = self.execute("cat /home/pi/quicksight/.env")
        if result["success"]:
            return self._parse_env(result["output"])
        return {}

    def _parse_env(self, content):
        """Parse .env file content"""
        env = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
        return env

    def write_env(self, env_dict):
        """Write .env file to Pi"""
        # Build env content
        content = "# ============ DASHBOARD KONFIG ============\n\n"
        content += f"DASHBOARD_MODE={env_dict.get('DASHBOARD_MODE', 'operations')}\n"
        content += f"CITY={env_dict.get('CITY', 'bergen')}\n"
        content += f"REFRESH_SECS={env_dict.get('REFRESH_SECS', '300')}\n"
        content += f"HEADLESS={env_dict.get('HEADLESS', 'false')}\n"
        content += f"USERNAME={env_dict.get('USERNAME', '')}\n"
        content += f"PASSWORD={env_dict.get('PASSWORD', '')}\n"
        if env_dict.get('THEME'):
            content += f"THEME={env_dict.get('THEME')}\n"

        # Write to file via echo (better than scp for small files)
        escaped = content.replace('"', '\\"').replace('\n', '\\n')
        cmd = f'echo -e "{escaped}" > /home/pi/quicksight/.env'

        return self.execute(cmd)

    def restart_service(self):
        """Restart quicksight systemctl service"""
        cmd = "sudo systemctl restart quicksight"
        return self.execute(cmd)

    def get_status(self):
        """Get service status"""
        cmd = "systemctl is-active quicksight"
        return self.execute(cmd)

    def get_logs(self, lines=20):
        """Get recent systemctl logs"""
        cmd = f"journalctl -u quicksight -n {lines} --no-pager"
        return self.execute(cmd)

    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()
