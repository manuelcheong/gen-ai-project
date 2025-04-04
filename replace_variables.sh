#!/bin/bash

# Usage information
usage() {
  echo "Usage: $0 -t TARGET_FILE -v VARIABLE_NAME -s SOURCE_FILE [-i INDENT_LEVEL] [-b BACKUP]"
  echo
  echo "Options:"
  echo "  -t TARGET_FILE   The file containing the variable to be replaced"
  echo "  -v VARIABLE_NAME The variable name to replace (without any prefix/suffix like $ or {})"
  echo "  -s SOURCE_FILE   The file containing the content to insert"
  echo "  -i INDENT_LEVEL  Optional: Number of spaces to indent the inserted content (default: auto-detect)"
  echo "  -b BACKUP        Optional: Create a backup of the target file with this extension"
  echo
  echo "Example: $0 -t template.yaml -v STATE_MACHINE_DEFINITION -s statemachine.json -i 8 -b .bak"
  exit 1
}

# Parse command line arguments
while getopts "t:v:s:i:b:" opt; do
  case $opt in
    t) TARGET_FILE="$OPTARG" ;;
    v) VARIABLE_NAME="$OPTARG" ;;
    s) SOURCE_FILE="$OPTARG" ;;
    i) INDENT_LEVEL="$OPTARG" ;;
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

# Auto-detect indentation if not specified
if [ -z "$INDENT_LEVEL" ]; then
  # Find the line with the variable
  VARIABLE_LINE=$(grep -n "\${$VARIABLE_NAME}" "$TARGET_FILE" | head -1 | cut -d: -f1)
  
  if [ -z "$VARIABLE_LINE" ]; then
    VARIABLE_LINE=$(grep -n "\$$VARIABLE_NAME" "$TARGET_FILE" | head -1 | cut -d: -f1)
  fi
  
  if [ -z "$VARIABLE_LINE" ]; then
    VARIABLE_LINE=$(grep -n "__${VARIABLE_NAME}__" "$TARGET_FILE" | head -1 | cut -d: -f1)
  fi
  
  if [ -z "$VARIABLE_LINE" ]; then
    echo "Error: Could not find variable '$VARIABLE_NAME' in target file"
    exit 1
  fi
  
  # Get the indentation of the line with the variable
  INDENT_STRING=$(sed -n "${VARIABLE_LINE}p" "$TARGET_FILE" | sed -E 's/^([[:space:]]*).*$/\1/')
  INDENT_LEVEL=${#INDENT_STRING}
  echo "Auto-detected indentation level: $INDENT_LEVEL spaces"
else
  echo "Using specified indentation level: $INDENT_LEVEL spaces"
fi

# Create indentation string
INDENT=$(printf '%*s' "$INDENT_LEVEL" '')

# Read the content from the source file and add indentation to each line
SOURCE_CONTENT=$(cat "$SOURCE_FILE" | sed "s/^/$INDENT/")

# Create a temporary file for processing
TEMP_FILE=$(mktemp)

# Process the target file line by line
while IFS= read -r line; do
  if [[ "$line" =~ \${$VARIABLE_NAME} ]] || [[ "$line" =~ \$$VARIABLE_NAME ]] || [[ "$line" =~ __${VARIABLE_NAME}__ ]]; then
    # Replace the variable with the indented content
    echo "$line" | sed -e "s/\${$VARIABLE_NAME}/$SOURCE_CONTENT/g" \
                       -e "s/\$$VARIABLE_NAME/$SOURCE_CONTENT/g" \
                       -e "s/__${VARIABLE_NAME}__/$SOURCE_CONTENT/g" >> "$TEMP_FILE"
  else
    # Keep the line as is
    echo "$line" >> "$TEMP_FILE"
  fi
done < "$TARGET_FILE"

# Replace the original file with the processed file
mv "$TEMP_FILE" "$TARGET_FILE"

echo "Successfully replaced '$VARIABLE_NAME' in '$TARGET_FILE' with properly indented content from '$SOURCE_FILE'"