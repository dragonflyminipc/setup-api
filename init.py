from typing import Dict, Union
import subprocess
import os
import re


def shell_command(command: str) -> Dict[str, Union[int, str]]:
    result = b""
    status = 0

    try:
        result = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as cmd_error:
        status = cmd_error.returncode
        result = cmd_error.output

    return {"status": status, "result": result.decode("utf-8")}


def print_success(text: str):
    print(f"\033[92m{text}\033[0m")


def print_warning(text: str):
    print(f"\033[93m{text}\033[0m")


def print_error(text: str):
    print(f"\033[91m{text}\033[0m")


def which_test(package: str) -> bool:
    result = shell_command(f"which {package}")

    return result["status"] == 0


def package_installed(package: str) -> bool:
    res = shell_command(f'dpkg -s {package} | grep "Status:"')

    if "install ok installed" in str(res["result"]):
        return True

    if which_test(package):
        return True

    return False


class HotspotInit:
    @classmethod
    def check_if_script_exists(cls, path):
        print(f"Checking if {path} exists")

        if os.path.exists(path):
            print(f"{path} exists")
            return

        print_warning(f"{path} doesn't exist, creating...")
        name = path.split("/")[-1]

        result = shell_command(f"sudo cp scripts/{name} {path}")

        if result["status"] != 0:
            print_error(f"Error while copying {name}: {result['result']}")
            raise Exception

        print(f"Successfully created {path}")

    @classmethod
    def check_script_permissions(cls, path):
        print(f"Checking {path} permissions")

        if os.access(path, os.X_OK):
            print(f"{path} has exec permissions")
            return

        print_warning(
            f"{path} doesn't have exec permissions, setting up permissions..."
        )

        result = shell_command(f"sudo chmod +x {path}")

        if result["status"] != 0:
            print_error(
                f"Error while setting write permissions to {path}: {result['result']}"
            )
            raise Exception

        print(f"Successfully set write permissions for {path}")

    @classmethod
    def check_execution(cls):
        print("Checking the execution of /usr/local/bin/get_hotspot_uuid.sh")

        result = shell_command("/usr/local/bin/get_hotspot_uuid.sh")

        if result["status"] != 0:
            print_error(
                f"Error while executing /usr/local/bin/get_hotspot_uuid.sh: {result['result']}"
            )
            raise Exception

        if not re.match(r"eqpayminer_[0-9a-f]{8}", result["result"]):
            print_error(
                f"Got unexpected output from /usr/local/bin/get_hotspot_uuid.sh: {result['result']}"
            )
            raise Exception

        print("/usr/local/bin/get_hotspot_uuid.sh output as expected")

        print("Checking the execution of /usr/local/bin/get_wifi_interface.sh")

        result = shell_command("/usr/local/bin/get_wifi_interface.sh")

        if result["status"] != 0:
            print_error(
                f"Error while executing /usr/local/bin/get_wifi_interface.sh: {result['result']}"
            )
            raise Exception

        if not re.match(r"^wl", result["result"]):
            print_error(
                f"Got unexpected output from /usr/local/bin/get_wifi_interface.sh: {result['result']}"
            )
            raise Exception

        print("/usr/local/bin/get_wifi_interface.sh output as expected")

        print(
            "Checking the execution of /usr/local/bin/get_ethernet_interface.sh"
        )

        result = shell_command("/usr/local/bin/get_ethernet_interface.sh")

        if result["status"] != 0:
            print_error(
                f"Error while executing /usr/local/bin/get_ethernet_interface.sh: {result['result']}"
            )
            raise Exception

        if not re.match(r"^e", result["result"]):
            print_error(
                f"Got unexpected output from /usr/local/bin/get_ethernet_interface.sh: {result['result']}"
            )
            raise Exception

        print("/usr/local/bin/get_ethernet_interface.sh output as expected")

    @classmethod
    def check_scripts(cls):
        print_warning("Checking hotspot scripts")

        cls.check_if_script_exists("/usr/local/bin/get_hotspot_uuid.sh")
        cls.check_script_permissions("/usr/local/bin/get_hotspot_uuid.sh")
        cls.check_if_script_exists("/usr/local/bin/get_wifi_interface.sh")
        cls.check_script_permissions("/usr/local/bin/get_wifi_interface.sh")
        cls.check_if_script_exists("/usr/local/bin/get_ethernet_interface.sh")
        cls.check_script_permissions("/usr/local/bin/get_ethernet_interface.sh")
        cls.check_if_script_exists("/usr/local/bin/start_hotspot.sh")
        cls.check_script_permissions("/usr/local/bin/start_hotspot.sh")

        cls.check_execution()

    @classmethod
    def check_service_files(cls):
        files = ["hotspot.service", "hotspot_restart.service"]

        for file in files:
            print_warning(f"Checking {file} file")
            path = f"/etc/systemd/system/{file}"
            print(f"Checking if {path} exists")

            if os.path.exists(f"{path}"):
                print(f"{path} exists")
                continue

            print_warning(f"{path} doesn't exist, creating...")

            result = shell_command(f"sudo cp scripts/{file} {path}")

            if result["status"] != 0:
                print_error(f"Error while copying {path}: {result['result']}")
                raise Exception

            print(f"Successfully created {path}")

    @classmethod
    def check_create_ap(cls):
        print_warning("Checking if create_ap is available")

        if not which_test("create_ap"):
            print_error("create_ap is not found")
            raise Exception

        print("create_ap is available")

    @classmethod
    def start_hotspot_service(cls):
        print_warning("Starting the hotspot service")

        print("Reloading the systemctl")
        result = shell_command("systemctl daemon-reload")

        if result["status"] != 0:
            print_error(
                f"Error while reloading the systemctl: {result['result']}"
            )
            raise Exception

        files = ["hotspot.service", "hotspot_restart.service"]

        for file in files:
            print(f"Starting the {file}")
            result = shell_command(f"systemctl restart {file}")

            if result["status"] != 0:
                print_error(
                    f"Error while starting the {file}: {result['result']}"
                )
                raise Exception

            print(f"Enabling the {file}")
            result = shell_command(f"systemctl enable {file}")

            if result["status"] != 0:
                print_error(
                    f"Error while enabling the {file}: {result['result']}"
                )
                raise Exception

    @classmethod
    def run(cls):
        print_warning("Setting up the hotspot")

        cls.check_scripts()
        cls.check_service_files()
        cls.check_create_ap()
        cls.start_hotspot_service()


class HotspotDepencendies:
    @classmethod
    def install_dependency(cls, package: str):
        print(f"Checking {package} dependency")

        if package_installed(package):
            print(f"{package} is already installed")

        else:
            os.system(f"sudo apt install -y {package}")

    @classmethod
    def install_dependencies(cls):
        dependencies = [
            "bash",
            "util-linux",
            "procps",
            "hostapd",
            "iproute2",
            "iw",
            "iwconfig",
            "libgtk-3-dev",
            "build-essential",
            "gcc",
            "g++",
            "pkg-config",
            "make",
            "libqrencode-dev",
            "libpng-dev",
        ]

        print_warning("Running hotspot dependency checks")

        for dependency in dependencies:
            cls.install_dependency(dependency)

    @classmethod
    def install_hotspot(cls):
        print_warning("Installing the hotspot")

        if package_installed("create_ap"):
            print("hotspot already installed")
            return

        current_work_dir = os.getcwd()

        os.chdir(os.path.expanduser("~"))
        os.system(
            "git clone https://github.com/lakinduakash/linux-wifi-hotspot.git"
        )
        os.chdir("linux-wifi-hotspot")
        os.system("sudo make install-cli-only")
        os.chdir(current_work_dir)

    @classmethod
    def run(cls):
        print_warning("Installing the hotspot")

        cls.install_dependencies()
        cls.install_hotspot()


class GeneralInit:
    @classmethod
    def check_directory(cls):
        print_warning("Checking the current directory")
        directory = os.getcwd()

        if directory == "/root/setup-api":
            print("The directory is correct, continuing...")
            return

        print_error(
            "The directory should be located at /root/setup-api.\n"
            "Please remove the current installation of the setup api "
            "and move it to the /root/ directory"
        )

        raise Exception

    @classmethod
    def apt_update(cls):
        os.system("sudo add-apt-repository -y universe")
        os.system("sudo apt-get update")

    @classmethod
    def install_dependency(cls, package: str):
        print(f"Checking {package} dependency")

        if package_installed(package):
            print(f"{package} is already installed")

        else:
            os.system(f"sudo apt install -y {package}")

    @classmethod
    def install_dependencies(cls):
        dependencies = [
            "git",
            "python3",
            "python3-dev",
            "python3-venv",
        ]

        print_warning("Running general dependency checks")

        for dependency in dependencies:
            cls.install_dependency(dependency)

        if not package_installed("pip3"):
            print_warning("Installing pip")
            os.system("wget https://bootstrap.pypa.io/get-pip.py")
            os.system("python3 get-pip.py")
            os.system("rm get-pip.py")

    @classmethod
    def run(cls):
        print_warning("Running the general initialization prodecures")

        cls.check_directory()
        cls.apt_update()
        cls.install_dependencies()


class PythonEnvSetup:
    @classmethod
    def create_venv(cls):
        print_warning("Creating a python virtual env")
        os.system("python3 -m venv venv")

    @classmethod
    def install_requirements(cls):
        print_warning("Installing requirements.txt")
        os.system("venv/bin/python3 -m pip install -r requirements.txt")

    @classmethod
    def move_config(cls):
        print_warning("Moving the config.py")
        os.system("cp docs/config.example.py config.py")

    @classmethod
    def run(cls):
        cls.create_venv()
        cls.install_requirements()
        cls.move_config()


class SetupApiInit:
    @classmethod
    def check_service_files(cls):
        files = ["setup_api.service"]

        for file in files:
            print_warning(f"Checking {file} file")
            path = f"/etc/systemd/system/{file}"
            print(f"Checking if {path} exists")

            if os.path.exists(f"{path}"):
                print(f"{path} exists")
                continue

            print_warning(f"{path} doesn't exist, creating...")

            result = shell_command(f"sudo cp scripts/{file} {path}")

            if result["status"] != 0:
                print_error(f"Error while copying {path}: {result['result']}")
                raise Exception

            print(f"Successfully created {path}")

    @classmethod
    def start_hotspot_service(cls):
        print_warning("Starting the hotspot service")

        print("Reloading the systemctl")
        result = shell_command("systemctl daemon-reload")

        if result["status"] != 0:
            print_error(
                f"Error while reloading the systemctl: {result['result']}"
            )
            raise Exception

        files = ["setup_api.service"]

        for file in files:
            print(f"Starting the {file}")
            result = shell_command(f"systemctl restart {file}")

            if result["status"] != 0:
                print_error(
                    f"Error while starting the {file}: {result['result']}"
                )
                raise Exception

            print(f"Enabling the {file}")
            result = shell_command(f"systemctl enable {file}")

            if result["status"] != 0:
                print_error(
                    f"Error while enabling the {file}: {result['result']}"
                )
                raise Exception

    @classmethod
    def run(cls):
        cls.check_service_files()
        cls.start_hotspot_service()


if __name__ == "__main__":
    GeneralInit.run()

    HotspotDepencendies.run()
    HotspotInit.run()

    PythonEnvSetup.run()
    SetupApiInit.run()
