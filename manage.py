#!/usr/bin/env python3
import subprocess
import sys
import secrets
import string

PROJECT_NAME = "bytebase"


def generate_clear_password(length=100):
    ambiguous = {'O', '0', 'I', 'l', '1'}
    alphabet = ''.join(c for c in (string.ascii_letters + string.digits) if c not in ambiguous)
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def parse_args(argv):
    args = {}
    key = None
    for item in argv:
        if item.startswith("--"):
            key = item.lstrip("-")
            args[key] = True  # default if no value provided
        elif key:
            args[key] = item
            key = None
    return args


def up():
    """Start docker compose services"""
    subprocess.run(["mkdir", "-p", f"/mnt/volume-db/{PROJECT_NAME}/postgress"], check=True)
    subprocess.run(["docker", "compose", "-p", PROJECT_NAME, "up", "-d"], check=True)


def down():
    """Stop docker compose services and remove volumes"""
    subprocess.run(["docker", "compose", "-p", PROJECT_NAME, "down", "-v"], check=True)


class ComposeApp:

    def __init__(self, action, user, host, protocol):
        self.action = action
        self.user = user
        self.host = host
        self.protocol = protocol
        self.env_variables = {
            'POSTGRES_USER': "bytebase_postgres_users",
            'POSTGRES_PASSWORD': generate_clear_password(),
            'POSTGRES_DB': "postgres",
            'OGNA_USER':user,
            'OGNA_HOST':host,
            'OGNA_PROTOCOL':protocol     
        }

    def configure(self):
        with open('.env', 'w+') as env_file:
            for key, value in self.env_variables.items():
                env_file.write(f"{key}={value}")
                env_file.write("\n")

    def deploy(self):
        self.configure()
        if self.action == "up":
            up()
        elif self.action == "down":
            down()
        else:
            print(f"Unknown command: {self.action}")
            print("Available commands: up, down")
            sys.exit(1)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    app = ComposeApp(
        action=args.get("action"),
        user=args.get("user", 'user'),
        host=args.get("host", 'localhost'),
        protocol=args.get("protocol", 'http')
    )

    app.deploy()
