function sparc-time-friendly () {

    local UTC_OFFSET_START
    local TIME_START_NO_OFFSET

    # gnu coreutils gdate needed for osx support/freebsd
    # gdate on darwin only has millisecond resolution?
    # this also won't work on freebsd without gnu coreutils
    iso8601millis="+%FT%T,%6N"  # FIXME do we _really_ need millis!? yemaybe? concurrent startups?
    utcoffset="+%:z"
    # I really hope the utc offset doesn't change between start & end
    # but laptops and airplains do exist, so it could
    # also how utterly annoying that the date separator and the
    # negative utc offset share the same symbol ... talk about
    # an annoying design flaw that is going to haunt humanity
    # with double the number of calls to date for # ... as
    # long as anoyone is writing code to deal with time
    TIME_START_NO_OFFSET=$(date ${iso8601millis} || gdate ${iso8601millis})
    UTC_OFFSET_START=$(date ${utcoffset} || gdate ${utcoffset})
    local TIME_START="${TIME_START_NO_OFFSET}${UTC_OFFSET_START}"  # XXX unused

    local TIME_START_NO_OFFSET_FS_OK=${TIME_START_NO_OFFSET//:/}
    local UTC_OFFSET_START_FS_OK=${UTC_OFFSET_START//:/}
    local TIME_START_FRIENDLY=${TIME_START_NO_OFFSET_FS_OK}${UTC_OFFSET_START_FS_OK}
    # So. iso8601 guidance on what to do about subsecond time and the utc offset in the compact
    # representation is not entirely clear, however I _think_ that %FT%T%H%M%S,%6N%z is ok but
    # the -/+ must stay between the timezone and the rest, so we will have to grab tz by itself
    local TIME_START_SAFE=${TIME_START_NO_OFFSET_FS_OK//-/}${UTC_OFFSET_START_FS_OK}  # XXX unused
    mv "$(mktemp --directory sparcur-all-XXXXXX)" "${TIME_START_FRIENDLY}" || \
        { CODE=$?; echo 'mv failed'; return $CODE; }
    echo "${TIME_START_FRIENDLY}"

}

function sparc-get-all-remote-data () {
    # NOTE not quite all the remote data, the google sheets
    # don't have caching functionality yet

    # parse args
    local POSITIONAL=()
    while [[ $# -gt 0 ]]
    do
    key="$1"
    case $key in # (ref:(((((((sigh)
        --project-id)         local PROJECT_ID="${2}"; shift; shift ;;
        --symlink-objects-to) local SYMLINK_OBJECTS_TO="${2}"; shift; shift ;;
        --log-path)           local LOG_PATH="${2}"; shift; shift ;;
        --parent-path)        local PARENT_PATH="${2}"; shift; shift ;;
        --only-filesystem)    local ONLY_FILESYSTEM="ONLY_FS"; shift ;;
        -h|--help)            echo "${HELP}"; return ;;
        *)                    POSITIONAL+=("$1"); shift ;;
    esac
    done

    # Why, you might be asking, are we declaring a local project path here without assignment?
    # Well. Let me tell you. Because local is a command with an exist status. So it _always_
    # returns zero. So if you need to check the output of the command running in a subshell
    # that you are assigning to a local variable _ALWAYS_ set local separately first.
    # Yes, shellcheck does warn about this. See also https://superuser.com/a/1103711
    local PROJECT_PATH

    if [[ -z "${PARENT_PATH}" ]]; then
        local PARENT_PATH
        set -o pipefail
        PARENT_PATH=$(sparc-time-friendly) || {
        CODE=$?;
        echo "Creating "'${PARENT_PATH}'" failed!"
        set +o pipefail
        return $CODE;
        }
        set +o pipefail
    fi

    local LOG_PATH=${LOG_PATH:-"${PARENT_PATH}/logs"}

    #local LOG_PATH=$(python -c "from sparcur.config import auth; print(auth.get_path('log-path'))")
    local PROJECT_ID=${PROJECT_ID:-$(python -c "from sparcur.config import auth; print(auth.get('remote-organization'))")}

    local maybe_slot=()
    if [[ -n "${SYMLINK_OBJECTS_TO}" ]]; then
        # MUST use arrays to capture optional arguments like this otherwise
        # arg values with spaces in them will destroy your sanity
        maybe_slot+=(--symlink-objects-to "${SYMLINK_OBJECTS_TO}")
    fi

    echo "${PARENT_PATH}"  # needed to be able to follow logs

    if [ ! -d "${LOG_PATH}" ]; then
        mkdir "${LOG_PATH}" || { CODE=$?; echo 'mkdir of ${LOG_PATH} failed'; return $CODE; }
    fi

    if [[ -z "${ONLY_FILESYSTEM}" ]]; then
        # fetch annotations (ref:bash-pipeline-fetch-annotations)
        echo "Fetching annotations metadata"
        python -m sparcur.simple.fetch_annotations > "${LOG_PATH}/fetch-annotations.log" 2>&1 &
        local pids_final[0]=$!

        # fetch remote metadata (ref:bash-pipeline-fetch-remote-metadata-all)
        # if this fails with 503 errors, check the
        # remote-backoff-factor config variable
        echo "Fetching remote metadata"
        python -m sparcur.simple.fetch_remote_metadata_all \
            --project-id "${PROJECT_ID}" \
            > "${LOG_PATH}/fetch-remote-metadata.log" 2>&1 &
        local pids[0]=$!
    fi

    local FAIL=0

    # clone aka fetch top level

    # we do not background this assignment because it runs quickly
    # and everything that follows depends on it finishing, plus we
    # need it to finish to set the PROJECT_PATH variable here
    echo python -m sparcur.simple.clone --project-id "${PROJECT_ID}" --parent-path "${PARENT_PATH}" "${maybe_slot[@]}"
    echo "Cloning top level"
    set -o pipefail
    PROJECT_PATH=$(python -m sparcur.simple.clone \
                          --project-id "${PROJECT_ID}" \
                          --parent-path "${PARENT_PATH}" \
                          "${maybe_slot[@]}" \
                          2>&1 | tee "${LOG_PATH}/clone.log" | tail -n 1) || {
        # TODO tee the output when verbose is passed
        CODE=$?;
        tail -n 100 "${LOG_PATH}/clone.log";
        echo "Clone failed! The last 100 lines of ${LOG_PATH}/clone.log are listed above.";
        apids=( "${pids[@]}" "${pids_final[@]}" );
        for pid in "${apids[@]}"; do
            kill $pid;
        done;
        set +o pipefail
        return $CODE;
    }
    set +o pipefail

    # explicit export of the current project path for pipelines
    # ideally we wouldn't need this, and when this pipeline
    # finished the export pipeline would kick off, or the export
    # pipeline would search for ... an existing project path ...
    # by ... oh right, looking for an environment variable or
    # checksing some other persistent state ... so this is the one
    # unless some controlling process sets it top down from the start
    # but we can't assume that
    export SPARCUR_PROJECT_PATH="${PROJECT_PATH}"

    for pid in "${pids[@]}"; do
        wait $pid || { FAIL=$((FAIL+1)); echo "${pid} failed!"; }
    done
    if [[ $FAIL -ne 0 || -z "${PROJECT_PATH}" ]]; then
        echo "${FAIL} commands failed. Cannot continue."
        echo "${PROJECT_PATH}"
        return 1
    fi

    # pull aka fetch file system metadata
    echo "Fetching file system metadata"
    echo python -m sparcur.simple.pull --project-path "${PROJECT_PATH}"
    python -m sparcur.simple.pull \
           --project-path "${PROJECT_PATH}" \
           > "${LOG_PATH}/pull.log" 2>&1 || {
        CODE=$?;
        tail -n 100 "${LOG_PATH}/pull.log";
        echo "Pull failed! The last 100 lines of ${LOG_PATH}/pull.log are listed above.";
        echo "${PROJECT_PATH}";
        return $CODE; }

    # fetch metadata files
    echo "Fetching metadata files"
    # have to pass project path as a position argument here so that it
    # does not try to pull aka fetch the file system metadata again
    echo python -m sparcur.simple.fetch_metadata_files --project-path "${PROJECT_PATH}"
    python -m sparcur.simple.fetch_metadata_files \
           --project-path "${PROJECT_PATH}" \
           > "${LOG_PATH}/fetch-metadata-files.log" 2>&1 &

    pids_final[1]=$!

    # fetch files
    echo "Fetching files"
    # XXX at some point this will probably also depend on the manifests
    # so we don't fetch everything with a matching extension
    # TODO derive --extension from manifests or all it to be passed in
    echo python -m sparcur.simple.fetch_metadata_files --project-path "${PROJECT_PATH}" --extension xml

    # FIXME fetch_files fails silently here :/
    python -m sparcur.simple.fetch_files \
           --project-path "${PROJECT_PATH}" \
           --extension xml \
           > "${LOG_PATH}/fetch-files.log" 2>&1 &

    pids_final[2]=$!

    local FAIL=0
    for pid in "${pids_final[@]}"; do
        wait $pid || { FAIL=$((FAIL+1)); echo "${pid} failed!"; }
    done

    # FIXME HACK
    #find -type f -size 0 -exec getfattr -d {} \;
    #find -type f -size 0 -exec spc fetch --limit=-1 {} \;

    if [[ $FAIL -ne 0 ]]; then
        echo "${FAIL} commands failed. Cannot continue."
        echo "${PROJECT_PATH}"
        return 1
    fi
    echo "All fetching completed successfully."

}

function sparc-export-all () {
    # parse args
    local POSITIONAL=()
    while [[ $# -gt 0 ]]
    do
    key="$1"
    case $key in # (ref:(((sigh)
        --project-path) local PROJECT_PATH="${2}"; shift; shift ;;
        -h|--help)      echo "${HELP}"; return ;;
        *)              POSITIONAL+=("$1"); shift ;;
    esac
    done

    local PROJECT_PATH="${PROJECT_PATH:-$SPARCUR_PROJECT_PATH}"
    spc export --project-path "${PROJECT_PATH}"
}

function sparc-export () {
    echo TODO not ready yet
    return 1
}

function sparc-fexport () {

    local DATASET_ID="${1}"
    local DATASET_UUID
    local DATASET_PATH
    local EXPORT_PATH

    DATASET_UUID="$(python -m sparcur.simple.utils --dataset-id ${DATASET_ID})"

    python -m sparcur.simple.retrieve --dataset-id ${DATASET_UUID} &&

    EXPORT_PATH="$(realpath "${DATASET_UUID}/exports")" &&
    DATASET_PATH="$(realpath "${DATASET_UUID}/dataset")" &&
    pushd "${DATASET_PATH}" &&

    # FIXME we shouldn't need this refetch so I think that retrieve is
    # broken if files/folders already exist
    python -m sparcur.cli find \
        --name '*.xml' \
        --name 'submission*' \
        --name 'code_description*' \
        --name 'dataset_description*' \
        --name 'subjects*' \
        --name 'samples*' \
        --name 'manifest*' \
        --name 'resources*' \
        --name 'README*' \
        --limit -1 \
        --fetch
    wait $!
    python -m sparcur.cli export --export-path "${EXPORT_PATH}" &  # FIXME TODO this conflates phases
    local pids[0]=$!
    # FIXME TODO for now export_single_dataset produces this so we don't run it independently
    # FIXME there is also a difference in the export folder because the path metadata targets
    # the last updated data and thus overwrites if the data has not changed but the code has
    #python -m sparcur.simple.path_metadata_validate --export-path "${EXPORT_PATH}" &
    #local pids[1]=$!
    local FAIL=0
    # TODO log/notify export failure

    for pid in "${pids[@]}"; do
        wait $pid || { FAIL=$((FAIL+1)); echo "${pid} failed!"; }
    done
    if [[ $FAIL -ne 0 ]]; then
        echo "${FAIL} commands failed. Cannot continue."
        echo "${DATASET_UUID}"
        echo "${DATASET_PATH}"
        return 1
    fi
    popd # or do it yourself because we might need to explore??
}
