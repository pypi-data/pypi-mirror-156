#!/bin/bash
set -e

show_help(){
    echo "Usage: ./install.sh command"
    echo "EXAMPLES:"
    echo "command : None                      { used for creating a build }"
    echo "command : dev                       { used for activating DEV mode }"
    exit
}

install_python3(){
    echo "Installing Python3..."
    apt update
    apt install -y python3
    apt install -y python3.8-venv
    echo "Python3 installed."
}

create_env_client(){
    PYTHON3=$(which python3)
    if [[ -z $PYTHON3 ]]; then
        install_python3
    fi
    echo "Creating ENVCLIENT..."
    rm -rf ENVCLIENT
    python3 -m venv ENVCLIENT
    source ENVCLIENT/bin/activate
    echo "ENVCLIENT creation finished."
}

delete_files(){
    # removing old files
    rm -rf .eggs build dist stadle_client.egg-info .pytest_cache
}

# install STADLE client
install_stadle_client(){
    echo "Upgrading pip..."
    pip install --upgrade pip
    echo "pip upgrade finished."

    echo "Setting Up STADLE..."
    python3 setup.py bdist_wheel
    python3 -m pip install dist/stadle_client-*-py3-none-any.whl --extra-index-url https://test.pypi.org/simple
    echo "STADLE setup finished."
}

activate_client_build(){
    delete_files
    create_env_client
    install_stadle_client
}

# argument check to get correct number of arguments
if [[ "$#" -gt 2 ]]; then
    echo "$# arguments provided"
    show_help
    exit

elif [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit

else
    # working with client setup
    echo "initializing setup for client build..."
    activate_client_build
    echo "client build finished."

    if [[ "$1" == "dev" ]]; then
        python3 setup.py develop
        pip install -e .[dev]
        echo "dev profile activated"
    fi
    exit
fi
