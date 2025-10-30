#!/bin/bash

# URLs
fhir_scripts_url="https://raw.githubusercontent.com/gematik/fhir-scripts/refs/heads/main/scripts/fhir_scripts.sh"
publisher_url="https://github.com/HL7/fhir-ig-publisher/releases/latest/download/publisher.jar"
publisher_jar="publisher.jar"
input_cache_path="$(pwd)/input-cache/"

###
# Log helpers
###
function log_info() {
    echo "➡️  $1"
}

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

function exec_exit_log_fail() {
    res=$($1 2>&1)
    if [[ $? -ne 0 ]]; then
        printf "$res\n"
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

function exec_succ_exit_log_fail() {
    res=$($1 2>&1)
    if [[ $? -eq 0 ]]; then
        log_succ "$2"
    else
        printf "$res\n"
        log_fail "$3"
        exit 1
    fi
}

function exec_succ_log_fail() {
    res=$($1 2>&1)
    if [[ $? -eq 0 ]]; then
        log_succ "$2"
    else
        printf "$res\n"
        log_fail "$3"
        return 1
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

###
# Print Versions
###
function print_versions() {
    # TODO script version
    echo "FSH Sushi: $(sushi_version)"
    echo "IG Publisher: $(igpub_version)"
    print_pytools_version
}

###
# Update
###
function update() {
    case "$1" in
        script) update_fhir_script ;;
        tools) update_tools ;;
        sushi) update_sushi ;;
        igpub) update_igpub ;;
        pytools) update_pytools ;;
        *)
            update_fhir_script
            update_tools
            update_pytools
        ;;

    esac
}

function update_script() {
    owner=$(ls -ld $2 | awk '{print $3}')
    if [[ $owner -ne $USER ]]; then
        # Needs root to set original owner
        exec_exit_log_fail "sudo curl -L $1 -o script.new.sh" "Failed to download latest version of $2"
        sudo mv script.new.sh $2
        sudo chown $owner $2
        sudo chmod +x $2
    else
        exec_exit_log_fail "curl -L $1 -o script.new.sh" "Failed to download latest version of $2"
        mv script.new.sh $2
        chmod +x $2
    fi

    log_succ "Updated $2"
}

function update_fhir_script() {
    update_script $fhir_scripts_url $0
}

function sushi_version() {
    sushi --version | sed -nE 's/SUSHI v([\.0-9]+).*/\1/p'
}

function update_sushi() {
    exec_succ_exit_log_fail "sudo npm install -g fsh-sushi" "Updated FSH Sushi to $(sushi_version)" "Failed to update FSH Sushi"
}

function igpub_version() {
    java -jar ${input_cache_path}${publisher_jar} -v
}

function _update_igpub() {
    curl -L "$publisher_url" -o "${input_cache_path}${publisher_jar}"
}

function update_igpub() {
    mkdir -p "$input_cache_path"
    exec_succ_exit_log_fail "_update_igpub" "Updated IG Publisher to $(igpub_version)" "Failed to update IG Publisher"
}

function update_tools() {
    update_sushi
    update_igpub
}

function update_pytool() {
    exec_succ_log_fail "sudo pipx install --global -f $1" "$2" "$3"
}

function print_pytools_version() {
    which epatools > /dev/null
    if [[ $? -eq 0 ]]; then
        echo "epatools: $(epatools_version)"
    fi

    which igtools > /dev/null
    if [[ $? -eq 0 ]]; then
        echo "igtools: $(igtools_version)"
    fi
}

function epatools_version() {
    which epatools > /dev/null
    if [[ $? -eq 0 ]]; then
        epatools --version
    fi
}

function igtools_version() {
    which igtools > /dev/null
    if [[ $? -eq 0 ]]; then
        igtools --version
    fi
}

function check_pytool_version() {
    local package_name="$1"
    local repo_url="$2"
    local current_version=""
    local latest_version=""
    local response=""

    # Handle missing parameters gracefully
    if [[ -z "$package_name" || -z "$repo_url" ]]; then
        echo "error:missing_parameters"
        return 0
    fi

    # Get current version from pipx
    current_version=$(sudo pipx list --global --short 2>/dev/null | awk -v pkg="$package_name" '$1 == pkg {print $2}') || true

    if [[ -z "$current_version" ]]; then
        echo "not_installed"
        return 0
    fi

    # Try to fetch latest version from GitHub with 1s timeout
    response=$(curl -s --connect-timeout 1 --max-time 1 "$repo_url" 2>/dev/null || true)

    if [[ -z "$response" ]]; then
        echo "error:fetch_failed_or_timeout:${current_version}"
        return 0
    fi

    # Try to find versions from filenames (dist/*.tar.gz, *.whl)
    latest_version=$(echo "$response" \
        | grep -Eo "${package_name}-[0-9]+(\.[0-9]+){1,2}(\.tar\.gz|\.whl)" \
        | sort -V \
        | tail -n 1 \
        | grep -Eo '[0-9]+(\.[0-9]+){1,2}' || true)

    # If not found, try to extract from __VERSION__ in source code listing
    if [[ -z "$latest_version" ]]; then
        latest_version=$(echo "$response" \
            | grep -Eo "__VERSION__\s*=\s*(Version\()?['\"][0-9]+(\.[0-9]+){1,2}['\"]\)?" \
            | sed -E "s/.*__VERSION__\s*=\s*(Version\()?['\"]([^'\"]+)['\"]\)?/\2/" \
            | sort -V \
            | tail -n 1 || true)
    fi

    if [[ -z "$latest_version" ]]; then
        echo "error:could_not_parse_latest_version:${current_version}"
        return 0
    fi

    # Compare installed vs. latest
    if [ "$current_version" = "$latest_version" ]; then
        echo "up_to_date:${current_version}"
    else
        echo "update_available:${current_version}:${latest_version}"
    fi

    return 0
}

function maintain_pytool() {
    local package_name=$1
    local check_url=$2
    local update_url=$3

    echo "Checking $package_name version"
    result=$(check_pytool_version "$package_name" "$check_url")
    IFS=':' read -r status current latest <<< "$result"

    case "$status" in
        update_available)
            echo "⬆️ $package_name: $current → $latest"
            update_pytool "$update_url" "Updated" "Failed to update $package_name"
            ;;
        up_to_date)
            echo "✅ $package_name up to date ($current)"
            ;;
        error*)
            echo "⚠️ $package_name check failed ($current)"
            ;;
        not_installed)
            echo "📦 $package_name not installed"
            ;;
    esac
}

function maintain_pytools() {
    maintain_pytool "epatools" \
        "https://api.github.com/repos/onyg/epa-tools/contents/dist" \
        "git+https://github.com/onyg/epa-tools.git"

    maintain_pytool "igtools" \
        "https://raw.githubusercontent.com/onyg/req-tooling/refs/heads/main/src/igtools/versioning.py" \
        "git+https://github.com/onyg/req-tooling.git"
}

function update_pytools() {
    update_pytool "git+https://github.com/onyg/epa-tools.git" "Updated epa-tools to $(epatools_version)" "Failed to update epa-tools"
    update_pytool "git+https://github.com/onyg/req-tooling.git" "Upated reqtooling to $(igtools_version)" "Failed to update req-tooling"
}

###
# Build
###
function build() {
    case "$1" in
        pytools)
            [[ "$UPDATE_PYTOOLS" == true ]] && maintain_pytools
            run_igtools
            merge_capabilities
        ;;
        sushi) run_sushi ;;
        defs)
            [[ "$UPDATE_PYTOOLS" == true ]] && maintain_pytools
            build_definitions
        ;;
        ig)
            [[ "$UPDATE_PYTOOLS" == true ]] && maintain_pytools
            build_ig
        ;;
        *)
            [[ "$UPDATE_PYTOOLS" == true ]] && maintain_pytools
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
    # Skip if igtools are not configured for the project
    if [[ ! -f "./.igtools/config.yaml" ]]; then
        return 0
    fi

    # Run if igtools are installed
    which igtools > /dev/null
    if [[ $? -ne 0 ]]; then
        log_warn "igtools not installed, skipping"
    else
        exec_succ_exit_log_fail "igtools process" "Processed requirement" "Failed to process requirement"
        exec_succ_exit_log_fail "igtools ig-release-notes input/data" "Created release-notes" "Failed to create release-notes"
        exec_succ_exit_log_fail "igtools export input/data" "Exported requirement" "Failed to export requirements"

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
        exec_succ_exit_log_fail "epatools merge" "CapabilityStatements merged" "Failed to merge CapabilityStatements"
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
        return 0
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
        log_warn "config file not found, skipping update of ZIP files"
        return 0
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
        log_info "Adding or replacing: $FILE in $ZIP"
        cp "./output/$FILE" "$TMPDIR/site"
        done

        # Repack zip with updated content
        cd "$TMPDIR"
        zip -qr ../full-ig.zip ./*
        cd - > /dev/null

        # Clean up
        rm -rf "$TMPDIR"

        log_succ "ZIP files updated successfully: $ZIP"
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
# Parse global flags
###
UPDATE_PYTOOLS=false
for arg in "$@"; do
  if [[ "$arg" == "-updatepytools" || "$arg" == "-u" ]]; then
    UPDATE_PYTOOLS=true
    # remove flag from arguments
    set -- "${@/-updatepytools/}"
    set -- "${@/-u/}"
    break
  fi
done

###
# Handle command-line argument or menu
###

case "$1" in
  update) update $2 ;;
  fhircache) rebuild_fhir_cache $2 ;;
  bdcache) delete_build_cache ;;
  build) build $2 ;;
  deploy) gcloud_deploy $2 ;;
  version) print_versions ;;
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

        if [[ "$UPDATE_PYTOOLS" == false && -t 0 && $# -eq 0 ]]; then

        default_choice="n"
        echo
        echo "Would you like to check for and install new pytool verions on the go?"
        echo -n "Enter y or n [default: n]: "
        read -t 15 choice || choice="$default_choice"
        choice="${choice:-$default_choice}"
        echo
        echo "You selected: $choice"
        echo
        if [[ "$choice" =~ ^[Yy]$ ]]; then
            UPDATE_PYTOOLS=true
        fi
        fi
        
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
                [[ "$UPDATE_PYTOOLS" == true ]] && maintain_pytools
                build_definitions
                build_ig
            ;;
            2)
                [[ "$UPDATE_PYTOOLS" == true ]] && maintain_pytools
                build_definitions ;;
            3)
                [[ "$UPDATE_PYTOOLS" == true ]] && maintain_pytools
                build_ig ;;
            0) exit 0 ;;
            *) echo "Invalid option." ;;
        esac
        ;;
      0) exit 0 ;;
      *) echo "Invalid option." ;;
    esac
  ;;

esac
