import requests
import zipfile
import os
import tempfile


class IBSelfUpdate:
    def __init__(
        self,
        program_path: str,
        retain: list = None,
        url: str = "http://localhost/",
        robot_name: str = "robot.zip",
        version_file_name: str = "version.txt",
    ) -> None:

        self.retain = retain
        self.url = url
        self.robot_name = robot_name
        self.version_file_name = version_file_name
        self.program_path = os.path.dirname(os.path.abspath(program_path))
        self.robot_path = os.path.join(self.program_path, "robot")
        self.__temp_files = {}

    def auto_update(
        self,
        verify_version: bool = True,
        backup_files: bool = True,
        download_file: bool = True,
        extract_file: bool = True,
        remove_file: bool = True,
    ):
        if verify_version:
            print("Verifying version")
            if self.verify_version():
                print("Already up to date")
                return

        if backup_files:
            print("Getting backup files")
            self.retain_files()

        if download_file:
            print("Getting new files")
            file_path = self.download_file(
                self.program_path, self.url + self.robot_name
            )

        if extract_file:
            print("Extracting")
            self.extract_file(file_path, self.program_path)

        if remove_file and download_file:
            print("Removing .zip")
            self.rm_file(file_path)

        if backup_files:
            print("Coping backup files")
            self.backup_files()

        print("Finished")

    def verify_version(self):
        local_version_path = os.path.join(self.robot_path, self.version_file_name)

        if not os.path.exists(local_version_path):
            return False

        with open(local_version_path, "r") as local_version_file:
            local_version = local_version_file.read()

        response = requests.get(self.url + self.version_file_name)
        remote_version = response.text

        print("Remote %s --> Local %s" % (remote_version, local_version))

        if local_version != remote_version:
            return False

        return True

    def retain_files(self):
        if not self.retain:
            return

        self.__temp_files = {}
        for file in self.retain:
            file_path = os.path.join(self.robot_path, file)

            if not os.path.exists(file_path):
                continue

            temp_file = tempfile.NamedTemporaryFile()
            self.__temp_files[file] = temp_file

            with open(file_path, "rb") as original:
                temp_file.write(original.read())

    def backup_files(self):
        for file in self.__temp_files:
            with open(os.path.join(self.robot_path, file), "wb") as backup:
                backup.write(self.__temp_files[file].read())

            self.__temp_files[file].close()

    @staticmethod
    def download_file(path, url):
        local_filename = url.split("/")[-1]

        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            file_path = os.path.join(path, local_filename)
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        return file_path

    @staticmethod
    def extract_file(file_path: str, to_dir_path: str):
        if os.path.exists(file_path):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(to_dir_path)
                return True
        return False

    @staticmethod
    def rm_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
