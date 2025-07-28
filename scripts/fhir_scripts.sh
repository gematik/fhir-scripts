#!/bin/bash

# URLs
fhir_scripts_url="https://raw.githubusercontent.com/cybernop/fhir-scripts/refs/heads/main/scripts/fhir_scripts.sh"
publisher_url="https://github.com/HL7/fhir-ig-publisher/releases/latest/download/publisher.jar"
publisher_jar="publisher.jar"
input_cache_path="$(pwd)/input-cache/"

function delete_build_cache() {
    rm -rf input-cache/schemas
    rm -rf input-cache/txcache
    echo "✅ Build cache cleared"
}

function update_script() {
    curl -L $1 -o "$2.new.sh" 2> /dev/null && mv "$2.new.sh" "$2.sh"
    chmod +x $2.sh
    echo "✅ Updated $2.sh"
}

function update_fhir_script() {
    update_script $fhir_scripts_url fhir_scripts
}

function update_tools() {
    sudo npm install -g fsh-sushi > /dev/null 2>&1
    retVal=$?
    if [[ $retVal -ne 0 ]]; then
        echo "❌ Failed to update FSH Sushi"
        exit 1
    fi
    echo "✅ Updated FSH Sushi to $(sushi --version | sed -nE 's/SUSHI v([\.0-9]+).*/\1/p')"
    mkdir -p "$input_cache_path"
    curl -L "$publisher_url" -o "${input_cache_path}${publisher_jar}" > /dev/null 2>&1
    retVal=$?
    if [[ $retVal -ne 0 ]]; then
        echo "❌ Failed to update IG Publisher"
        exit 1
    fi
    echo "✅ Updated IG Publisher to $(java -jar ${input_cache_path}${publisher_jar} -v)"
}

function update_pytools() {
    sudo pipx install --global -f git+https://github.com/onyg/epa-tools.git
    sudo pipx install --global -f git+https://github.com/onyg/req-tooling.git
}

function rebuild_fhir_cache() {
    rm -rf $HOME/.fhir/packages/*
    echo "✅ Cache cleared"
    echo

    if [[ ! -z ${1+x} ]]; then

        deps=$(jq -c '.dependencies | to_entries' ./package.json)
        echo $deps | jq -cr '.[]' | while read dep ; do
            # save previous version of 'package.json'
            mv package.json package.tmp.json && echo "{}" > package.json

            # extract the package and version
            pkg=$(echo $dep | jq -r '.key')
            version=$(echo $dep | jq -r '.value')

            # check if file exists
            file=${1}/${pkg}_${version}.tgz
            if [[ ! -f "$file" ]]; then
                file=${1}/${pkg}-${version}.tgz
                if [[ ! -f "$file" ]]; then
                    npm --registry https://packages.simplifier.net pack --pack-destination $1 ${pkg}@${version} 2> /dev/null
                    if [[ -f "$file" ]]; then
                        echo "✅ Downloaded package ${pkg}@${version} to local package directory"
                    else
                        echo "⚠️ Could not download package ${pkg}@${version}"
                        unset file
                    fi
                fi
            fi

            # install local package if exists
            if [[ ! -z ${file+x} ]]; then
                fhir install $file --file > /dev/null

                retVal=$?
                if [[ $retVal -eq 0 ]]; then
                    echo "✅ Installed ${pkg}@${version}"
                else
                    echo "❌ Failed to install ${pkg}@${version}"
                fi
            fi

            # restore previous version of 'package.json'
            mv -f package.tmp.json package.json
        done
        echo
    fi

    fhir restore
    retVal=$?

    echo
    if [[ $retVal -eq 0 ]]; then
        echo "✅ Rebuilt complete"
    else
        echo "❌ Rebuilt failed"
    fi
}

function gcloud_deploy() {
    config_file="$(dirname "$0")/deploy.config.sh"
    if [[ -f $config_file ]]; then
        . "$(dirname "$0")/deploy.config.sh"
    else
        echo "❌ Error: config file not found"
    fi

    gcloud_login

    case "$1" in
        dev) BUCKET_NAME=${BUCKET_NAME_DEV} ;;
        prod) BUCKET_NAME=${BUCKET_NAME_PROD} ;;
        *)
            echo "❌ Error: Set environment 'dev' or 'prod'."
            exit 1
        ;;

    esac

    target_path="${BUCKET_NAME}${BUCKET_PATH}/${TARGET}"

    echo "✅ TARGET PATH: $target_path"

    if gsutil ls gs://$target_path > /dev/null 2>&1; then
        echo "TARGET directory already exists: ${target_path}"
        gcloud_rm $target_path
    else
        echo "TARGET directory does not exist"
    fi

    gcloud_cp $target_path
}

function gcloud_login() {
    if echo "" | gcloud projects list &> /dev/null; then
        :
    else
        gcloud auth login
    fi
}

function gcloud_rm() {
    echo "Deleting existing TARGET: $1"
    gcloud storage rm --recursive gs://$1
}

function gcloud_cp() {
    echo "Uploading new version to TARGET: $1"
    gsutil -m -h "Cache-Control:no-cache" cp -r ./output/* gs://$1
}

# Handle command-line argument or menu
case "$1" in
  update) update_fhir_script ;;
  pytools) update_pytools ;;
  tools) update_tools ;;
  fhircache) rebuild_fhir_cache $2 ;;
  bdcache) delete_build_cache ;;
  deploy) gcloud_deploy $2 ;;
  exit) exit 0 ;;
  *)
    # Compute default choice
    default_choice=0 # Exit on default

    echo "Please select an option:"
    echo "1) Update script"
    echo "2) Update pytools"
    echo "3) Update FHIR tools"
    echo "4) Rebuild FHIR cache"
    echo "5) Delete build cache"
    echo "0) Exit"
    echo

    # Read with timeout, but default if nothing entered
    echo -n "Choose an option [default: $default_choice]: "
    read -t 5 choice || choice="$default_choice"
    choice="${choice:-$default_choice}"
    echo "You selected: $choice"

    case "$choice" in
      1) update_fhir_script ;;
      2) update_pytools ;;
      3) update_tools ;;
      4) rebuild_fhir_cache ;;
      5) delete_build_cache ;;
      0) exit 0 ;;
      *) echo "Invalid option." ;;
    esac
  ;;

esac
