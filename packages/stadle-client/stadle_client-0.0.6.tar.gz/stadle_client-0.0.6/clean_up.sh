#!/bin/bash
set -e
#   This script should be used to clean up existing envs or build files.
#   This might be modified later to include execution on the server as well.
#   No immediate plans though
#

show_help(){
    echo "Usage: ./clean_up.sh <command>"
    echo "EXAMPLES:"
    echo "command : envs       { used for deleting various environments }"
    echo "command : build      { used for deleting various build specific folders }"
    echo "command : all        { used for deleting everything }"
    exit
}

# delete environments
if [[ "$1" == "envs" ]]; then
    echo "Removing various environments to initiate a new build ENV"

    rm -rf ENVSTADLE ENVCLIENT ENVDEPLOY

    echo "ENVs Removed!"

# delete build specific folders
elif [[ "$1" == "build" ]]; then
    echo "Removing various environments to initiate a new build ENV"

    rm -rf build dist .eggs stadle_client.egg-info .pytest_cache

    echo "build files/folders deleted!"

# delete all
elif [[ "$1" == "all" ]]; then
    echo "Removing everything"

    rm -rf ENVSTADLE ENVCLIENT ENVDEPLOY
    rm -rf build dist .eggs stadle_client.egg-info .pytest_cache

    echo "Everything Removed!"

# erroneous arguments
else
    echo "unknown parameters provided"
    show_help
    exit
fi