#!/bin/bash

set -e

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# declare -A images
# 
# images=(["flask"]="pier:5000/gps-server" \
#         ["flask"]="pier:5000/gps-celery" \
#         ["GpsJenkinsSlave"]="pier:5000/gps-jenkins-slave")

images=( "flask" "haproxy" "mongo" )

for image in "${images[@]}"
do
    echo "Building ${image}"
    docker build -t "${image}" "${ROOT_DIR}/${image}"
done

