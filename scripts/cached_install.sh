#!/bin/bash

function install_package_cached() {
    # Get the package name and version
    pkg_split=(${1//@/ })
    pkg=${pkg_split[0]}
    ver=${pkg_split[1]}

    # Build file path
    file=$2/${pkg}-${ver}.tgz

    # Download package
    if [[ -f "$file" ]]; then
        echo "Using cached package from $file"
    else
        echo "Downloading package to $file"
        npm --registry https://packages.simplifier.net pack --pack-destination ${down_dir} $1 2> /dev/null
    fi

    # Install
    echo "Installing package $1"
    mv package.json package.json_
    fhir install ${file} --file
    mv package.json_ package.json
}



install_package_cached hl7.fhir.r4.core@4.0.1 ~/fhir-packages
