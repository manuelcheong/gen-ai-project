#!/bin/bash

# Usage information
usage() {
  echo "Usage: $0 -t TARGET_FILE -v VARIABLE_NAME -s SOURCE_FILE [-b BACKUP]"
  echo
  echo "Options:"
  echo "  -t TARGET_FILE   The file containing the variable to be replaced"
  echo "  -v VARIABLE_NAME The variable name to replace (without any prefix/suffix like $ or {})"
  echo "  -s SOURCE_FILE   The file containing the content to insert"
  echo "  -b BACKUP        Optional: Create a backup of the target file with this extension"
  echo
  echo "Example: $0 -t template.yaml -v STATE_MACHINE_DEFINITION -s statemachine.json -b .bak"
  exit 1
}

# Parse command line arguments
while getopts "t:v:s:b:" opt; do
  case $opt in
    t) TARGET_FILE="$OPTARG" ;;
    v) VARIABLE_NAME="$OPTARG" ;;
    s) SOURCE_FILE="$OPTARG" ;;
    b) BACKUP="$OPTARG" ;;
    *) usage ;;
  esac
done

# Check if required parameters are provided
if [ -z "$TARGET_FILE" ] || [ -z "$VARIABLE_NAME" ] || [ -z "$SOURCE_FILE" ]; then
  echo "Error: Missing required parameters"
  usage
fi

# Check if files exist
if [ ! -f "$TARGET_FILE" ]; then
  echo "Error: Target file '$TARGET_FILE' not found"
  exit 1
fi

if [ ! -f "$SOURCE_FILE" ]; then
  echo "Error: Source file '$SOURCE_FILE' not found"
  exit 1
fi

# Create backup if requested
if [ ! -z "$BACKUP" ]; then
  cp "$TARGET_FILE" "${TARGET_FILE}${BACKUP}"
  echo "Created backup: ${TARGET_FILE}${BACKUP}"
fi

# Read the content from the source file
SOURCE_CONTENT=$(cat "$SOURCE_FILE")

# Escape special characters for sed
# This handles newlines, backslashes, forward slashes, and ampersands
ESCAPED_CONTENT=$(echo "$SOURCE_CONTENT" | sed -e ':a' -e 'N' -e '$!ba' -e 's/\\/\\\\/g' -e 's/\//\\\//g' -e 's/&/\\\&/g' -e 's/\n/\\n/g')

# Replace the variable in the target file
# We look for the variable in different formats: ${VARIABLE}, $VARIABLE, or __VARIABLE__
sed -i.tmp -e "s/\${$VARIABLE_NAME}/$ESCAPED_CONTENT/g" \
           -e "s/\$$VARIABLE_NAME/$ESCAPED_CONTENT/g" \
           -e "s/__${VARIABLE_NAME}__/$ESCAPED_CONTENT/g" "$TARGET_FILE"

# Remove the temporary file created by sed
rm "${TARGET_FILE}.tmp"

echo "Successfully replaced '$VARIABLE_NAME' in '$TARGET_FILE' with content from '$SOURCE_FILE'"
