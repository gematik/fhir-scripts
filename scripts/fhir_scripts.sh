#!/bin/bash

# URLs
fhir_scripts_url="https://raw.githubusercontent.com/cybernop/fhir-scripts/refs/heads/main/scripts/fhir_scripts.sh"
publisher_url="https://github.com/HL7/fhir-ig-publisher/releases/latest/download/publisher.jar"
publisher_jar="publisher.jar"
input_cache_path="$(pwd)/input-cache/"

###
# Log helpers
###
function log_succ() {
    echo "✅ $1"
}

function log_fail() {
    echo "❌ $1"
}

function log_warn() {
    echo "⚠️ $1"
}

###
# Workflow helpers
###
function check_fail() {
    if [[ $1 -ne 0 ]]; then
        log_fail "$2"
    fi
}

function check_exit_fail() {
    if [[ $1 -ne 0 ]]; then
        log_fail "$2"
        exit 1
    fi
}

function check_succ_fail() {
    if [[ $1 -eq 0 ]]; then
        log_succ "$2"
    else
        log_fail "$3"
    fi
}

function check_succ_exit_fail() {
    if [[ $1 -eq 0 ]]; then
        log_succ "$2"
    else
        log_fail "$3"
        exit 1
    fi
}

###
# Command functions
###
function delete_build_cache() {
    rm -rf input-cache/schemas
    rm -rf input-cache/txcache
    log_succ "Build cache cleared"
}

function update_script() {
    curl -L $1 -o "$2.new.sh" 2> /dev/null && mv "$2.new.sh" "$2.sh"
    check_exit_fail $? "Failed to download latest version of $2"

    chmod +x $2.sh
    check_exit_fail $? "Failed to set permission of $2"

    log_succ "Updated $2.sh"
}

function update_fhir_script() {
    update_script $fhir_scripts_url fhir_scripts
}

function update_tools() {
    sudo npm install -g fsh-sushi > /dev/null 2>&1
    check_exit_fail $? "Failed to update FSH Sushi"

    log_succ "Updated FSH Sushi to $(sushi --version | sed -nE 's/SUSHI v([\.0-9]+).*/\1/p')"
    mkdir -p "$input_cache_path"
    curl -L "$publisher_url" -o "${input_cache_path}${publisher_jar}" > /dev/null 2>&1
    check_exit_fail $? "Failed to update IG Publisher"

    log_succ "Updated IG Publisher to $(java -jar ${input_cache_path}${publisher_jar} -v)"
}

function update_pytools() {
    sudo pipx install --global -f git+https://github.com/onyg/epa-tools.git
    check_succ_fail $? "Updated epa-tools" "Failed to update epa-tools"

    sudo pipx install --global -f git+https://github.com/onyg/req-tooling.git
    check_succ_exit_fail $? "Upated reqtooling" "Failed to update req-tooling"
}

###
# Build
###
function build() {
    case "$1" in
        noig) build_definitions ;;
        nodefs) build_ig ;;
        *)
            build_definitions
            build_ig
        ;;

    esac
}

###
# Build definitions
###
function build_definitions() {
    run_igtools
    run_sushi
    merge_capabilities
}

function run_igtools() {
    # Run if igtools are installed
    which igtools > /dev/null
    if [[ $? -ne 0 ]]; then
        log_warn "igtools not installed, skipping"
    else
        igtools process > /dev/null
        check_succ_exit_fail $? "Processed requirement" "Failed to process requirement"

        igtools ig-release-notes input/data > /dev/null
        check_succ_exit_fail $? "Created release-notes" "Failed to create release-notes"

        igtools export input/data > /dev/null
        check_succ_exit_fail $? "Exported requirement" "Failed to export requirements"

        echo
        log_succ "All igtools commands executed successfully"
    fi
}

function run_sushi() {
    echo
    sushi
    check_succ_exit_fail $? "Sushi run successful" "Sushi run failed"
}

function merge_capabilities() {
    # Run if epatools are installed
    echo
    which epatools > /dev/null
    if [[ $? -ne 0 ]]; then
        log_warn "epatools not installed, skipping"
    else
        epatools merge > /dev/null
        check_succ_exit_fail $? "CapabilityStatements merged" "Failed to merge CapabilityStatements"
    fi
}

###
# Build IG
###
function build_ig() {
    run_ig_pub
    generate_openapi
    zip_content
    qa_results
}

function run_ig_pub() {
    config_file="./config.sh"
    if [[ -f $config_file ]]; then
        . $config_file
    else
        log_fail "Error: config file not found"
        exit 1
    fi

    if [[ -f "${input_cache_path}${publisher_jar}" ]]; then
        java -jar ${input_cache_path}${publisher_jar} -no-sushi -ig . -publish $PUBLISH_URL
        check_succ_exit_fail $? "Built IG" "Failed to build IG"
    else
        log_fail "IG Publisher not found"
        exit 1
    fi
}

function generate_openapi() {
    echo
    which epatools > /dev/null
    if [[ $? -ne 0 ]]; then
        log_warn "epatools not installed, skipping"
    else
        epatools openapi
        retVal=$?
        echo
        check_succ_exit_fail $retVal "OpenAPI(s) generated" "Failed to generate OpenAPI(s)"
    fi
}

function zip_content() {
    config_file="./config.sh"
    if [[ -f $config_file ]]; then
        . $config_file
    else
        log_fail "Error: config file not found"
        exit 1
    fi

    echo
    if [[ -z ${CONTENT_FILES+x} ]]; then
        log_warn "'CONTENT_FILES' not defined, skipping"
    else
        # Define path to zip and working files
        ZIP="./output/full-ig.zip"
        TMPDIR="./output/tmp_zip_edit"

        # Clean and create temporary directory
        rm -rf "$TMPDIR"
        mkdir -p "$TMPDIR"

        # Unzip current ig.zip to temp directory
        unzip -q "$ZIP" -d "$TMPDIR"

        # Copy each file into the unzipped content
        for FILE in "${CONTENT_FILES[@]}"; do
        echo "➡️  Adding or replacing: $FILE in $ZIP"
        cp "./output/$FILE" "$TMPDIR/site"
        done

        # Repack zip with updated content
        cd "$TMPDIR"
        zip -qr ../full-ig.zip ./*
        cd - > /dev/null

        # Clean up
        rm -rf "$TMPDIR"

        echo "✅ ZIP files updated successfully: $ZIP"
    fi
}

function qa_results() {
    echo
    echo "IG QA Result: errors = $(jq '.errs' output/qa.json), warnings = $(jq '.warnings' output/qa.json), hints = $(jq '.hints' output/qa.json)"
}


###
# Rebuild FHIR cache
###
function rebuild_fhir_cache() {
    rm -rf $HOME/.fhir/packages/*
    log_succ "Cache cleared"
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
                        log_succ "Downloaded package ${pkg}@${version} to local package directory"
                    else
                        log_warn "Could not download package ${pkg}@${version}"
                        unset file
                    fi
                fi
            fi

            # install local package if exists
            if [[ ! -z ${file+x} ]]; then
                fhir install $file --file > /dev/null
                check_succ_fail $? "Installed ${pkg}@${version}" "Failed to install ${pkg}@${version}"
            fi

            # restore previous version of 'package.json'
            mv -f package.tmp.json package.json
        done
        echo
    fi

    fhir restore
    retVal=$?

    echo
    check_succ_fail $retVal "Rebuilt complete" "Rebuilt failed"
}

###
# Deploy
###
function gcloud_deploy() {
    config_file="./config.sh"
    if [[ -f $config_file ]]; then
        . $config_file
    else
        log_fail "Error: config file not found"
        exit 1
    fi

    gcloud_login

    case "$1" in
        dev) BUCKET_NAME=${BUCKET_NAME_DEV} ;;
        prod) BUCKET_NAME=${BUCKET_NAME_PROD} ;;
        *)
            log_fail "Error: Set environment 'dev' or 'prod'."
            exit 1
        ;;

    esac

    target_path="${BUCKET_NAME}${BUCKET_PATH}/${TARGET}"

    log_succ "TARGET PATH: $target_path"

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

###
# Handle command-line argument or menu
###
case "$1" in
  update) update_fhir_script ;;
  pytools) update_pytools ;;
  tools) update_tools ;;
  fhircache) rebuild_fhir_cache $2 ;;
  bdcache) delete_build_cache ;;
  build) build $2 ;;
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
    echo "6) Build"
    echo "0) Exit"
    echo

    # Read with timeout, but default if nothing entered
    echo -n "Choose an option [default: $default_choice]: "
    read -t 30 choice || choice="$default_choice"
    choice="${choice:-$default_choice}"
    echo "You selected: $choice"

    case "$choice" in
      1) update_fhir_script ;;
      2) update_pytools ;;
      3) update_tools ;;
      4) rebuild_fhir_cache ;;
      5) delete_build_cache ;;
      6)
        default_choice=0 # Exit on default

        echo "Please select an option:"
        echo "1) Build everything"
        echo "2) Build only definition"
        echo "3) Build only IG"
        echo "0) Exit"
        echo

        # Read with timeout, but default if nothing entered
        echo -n "Choose an option [default: $default_choice]: "
        read -t 30 choice || choice="$default_choice"
        choice="${choice:-$default_choice}"
        echo "You selected: $choice"

        case "$choice" in
            1)
                build_definitions
                build_ig
            ;;
            2) build_definitions ;;
            3) build_ig ;;
            0) exit 0 ;;
            *) echo "Invalid option." ;;
        esac
        ;;
      0) exit 0 ;;
      *) echo "Invalid option." ;;
    esac
  ;;

esac
