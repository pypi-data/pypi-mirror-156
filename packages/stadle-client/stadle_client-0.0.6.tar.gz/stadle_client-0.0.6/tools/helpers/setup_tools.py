import os
import pathlib


class InstallationTools:
    """[summary]
        This class provides functionalities to retrieve architecture specific requirements to setup STADLE.
    """

    def __init__(self, forced_arch=None) -> None:
        """[summary]
            Initialise some variables and set path for requirement files.
        """
        # associated with various architecture types supported by STADLE with dedicated requirement_files
        self.supported_archs = ["arm64", "x86_64", "aarch64"]

        # set stadle_dev as base path
        self.base_path = pathlib.Path(__file__).parent.absolute().parent.parent
        # set requirements folder path
        if "\\" in str(self.base_path): # to check if the generated path is WindowsPath type or not
            self.requirement_path = os.path.join(self.base_path, "requirements\\stadle\\")
        else:
            self.requirement_path = os.path.join(self.base_path, "requirements/stadle/")

        try:
            # set system architecture
            self.system_arch = os.popen("arch").readlines()[0].strip("\n")
            print(f"System Architecture identified: {self.system_arch}")
        except:
            self.system_arch = "basic"
        else:
            if self.system_arch not in self.supported_archs:
                self.system_arch = "basic"

        if forced_arch is not None:
            self.system_arch = forced_arch
        print(f"System Architecture set for installation: {self.system_arch}")

    def get_install_requires(self) -> list:
        """[summary]
            Used in setup.py to fill up required packages needed for standard installation
        Returns:
            str: [package names stored in requirement file]
        """
        filename = "install_" + self.system_arch + ".txt"
        filename = os.path.join(self.requirement_path, filename)
        return self.file_reader(file_path=filename)
    
    def get_dev_requires(self) -> list:
        """[summary]
            Used in setup.py to fill up required packages needed for dev set up
        Returns:
            str: [package names stored in requirement file for dev set up]
        """
        filename = "dev_requires_" + self.system_arch + ".txt"
        filename = os.path.join(self.requirement_path, filename)
        return self.file_reader(file_path=filename)

    def file_reader(self, file_path) -> list:
        """[summary]
            Used by other methods to safely read files
        Args:
            file_path ([str]): [path to file that needs reading]
        Raises:
            OSError: [file reading error]
            FileNotFoundError: [file path provided does not exist]
        Returns:
            list: [package name]
        """
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r") as file_handler:
                    file_content =  file_handler.readlines()
                file_content = [package_name.strip("\n") for package_name in file_content]
                return file_content
            except:
                raise OSError(f"Exception while reading {file_path}")
        else:
            raise FileNotFoundError(f"File not found : {file_path}")

    def read_file_as_text(self, file_path) -> str:
        """[summary]
            Used to read any file as a single string
        Args:
            file_path ([pasixPath]): [path of the file to be read]
        Returns:
            str: [contents of read file]
        """
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r") as file_handler:
                    file_content =  file_handler.read()
                return file_content
            except:
                raise OSError(f"Exception while reading {file_path}")
        else:
            raise FileNotFoundError(f"File not found : {file_path}")
        

# this function can be used for manual debugging and testing this file
if __name__ == '__main__':
    object = InstallationTools()
    print(object.requirement_path)
