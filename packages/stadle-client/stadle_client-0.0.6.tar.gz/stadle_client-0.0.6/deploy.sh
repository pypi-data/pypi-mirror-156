#!/bin/bash
set -e

show_help(){
    echo "Usage: ./deploy.sh -- creates deployables and sends them to private pypi server"
    exit
}

install_python3(){
    echo "Installing Python3..."
    apt update
    apt install -y python3
    apt install -y python3.8-venv
    echo "Python3 installed."
}

create_env_deploy(){
    PYTHON3=$(which python3)
    if [[ -z $PYTHON3 ]]; then
        install_python3
    fi
    echo "Creating ENVDEPLOY..."
    rm -rf ENVDEPLOY
    python3 -m venv ENVDEPLOY
    source ENVDEPLOY/bin/activate
    echo "ENVDEPLOY creation finished."
}

install_deploy_requirements(){
    echo "Upgrading pip..."
    pip install --upgrade pip
    echo "pip upgrade finished."
    pip install twine
}

build_stadle_client(){
    echo "Building stadle client..."
    python3 setup.py bdist_wheel
    python3 setup.py sdist
    echo "stadle client built."
}

deploy_to_pypi_private(){
    IP_address="3.110.171.230"
    PORT="8080"
    twine upload --verbose --repository-url http://$IP_address:$PORT dist/*
    echo "Upload complete. "
}

deploy_to_pypi(){
    IP_address="3.110.171.230"
    PORT="8080"
    twine upload --verbose dist/*
    echo "Upload complete. "
}

deploy_to_test_pypi(){
    IP_address="3.110.171.230"
    PORT="8080"
    twine upload --verbose --repository testpypi dist/*
    echo "Upload complete. "
}

install_from_pypi(){
    IP_address="3.110.171.230"
    PORT="8080"
    pip install --index-url http://$IP_address:$PORT stadle_client --trusted-host $IP_address
    echo "Install complete."
}

clean_up(){
    # removing old files
    rm -rf .eggs build dist stadle_client.egg-info ENVDEPLOY
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
    clean_up
    create_env_deploy
    install_deploy_requirements
    build_stadle_client
    # deploy_to_pypi_private
    deploy_to_test_pypi
    deploy_to_pypi
    clean_up
fi