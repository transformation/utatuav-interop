#!/bin/bash

# Format all files changed sinced commit-ish.
# Untracked files will not be formatted, but any committed, staged
# or unstaged (but tracked) files will be.

# This directory
tools=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
# Base repo directory
repo=$(readlink -f ${tools}/..)

# Diff against master by default
commitish=master

if [[ "$1" != "" ]]; then
    commitish="$1"
fi

# Run all files (A)dded, (C)opied, (M)odified, (R)emaned, or changed (T)
# through the formatter.
git diff --name-status --diff-filter=ACMRT ${commitish} |
    cut -f 2 |        # Filename only (git diff gives 'A tools/format.sh')
    grep '\.py$' |    # Python files only
    xargs -i yapf -i "${repo}/{}"
