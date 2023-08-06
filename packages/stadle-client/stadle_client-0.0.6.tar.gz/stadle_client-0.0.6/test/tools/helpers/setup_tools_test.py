import os.path

from pytest import raises
from tools.helpers.setup_tools import InstallationTools

# class_object used for testing 
class_object = InstallationTools()

def test_class_init():
    # basic check to assure various paths are being set correctly to the base of stadle_dir
    base_path = str(class_object.base_path).split("/")[-1]
    base_path_windows = str(class_object.base_path).split("\\")[-1]
    assert base_path == "stadle_client" or base_path_windows == "stadle_client"

    requirement_path = "/".join(str(class_object.requirement_path).split("/")[-4:])
    requirement_path_windows = "\\".join(str(class_object.requirement_path).split("\\")[-4:])
    assert requirement_path == "stadle_client/requirements/stadle/" or requirement_path_windows == "stadle_client\\requirements\\stadle\\"

    # check if the existing system arch is supported by stadle
    # assert class_object.system_arch in class_object.supported_archs

def test_get_install_requires():
    # basic check to make sure that output is a list
    requirements = class_object.get_install_requires()
    assert type(requirements) is list

    # check if some required packages are in the returned list
    for index in range(len(requirements)):
        requirements[index] = requirements[index].split("==")[0]
    assert "click" in requirements
    assert "websockets" in requirements
    assert "numpy" in requirements

def test_get_dev_requires():
    # basic check to make sure that output is a list
    requirements = class_object.get_dev_requires()
    assert type(requirements) is list

    # check if some required packages are in the returned list
    for index in range(len(requirements)):
        requirements[index] = requirements[index].split("==")[0]
    assert "check-manifest" in requirements
    assert "twine" in requirements

def test_file_reader():
    # check if the read file is str to make sure the file is read, if it exists
    file_path = os.path.join(class_object.requirement_path, "install_basic.txt")
    assert type(class_object.file_reader(file_path=file_path)) is list
    
    # throws FileNotFoundError if file doesn't exist
    file_path = os.path.join(class_object.requirement_path, "non-existent-file.txt")
    with raises(FileNotFoundError):
        class_object.file_reader(file_path=file_path)

    # very difficult to make a test for OSError as the criteria are too troublesome to replicate 
    # need to look into this some day, NON BLOCKING
