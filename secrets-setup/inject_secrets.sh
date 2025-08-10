#! /bin/bash
set -o allexport
source "../.env"
set +o allexport

# Get a bw login session
bw login --apikey
export BW_SESSION=$(bw unlock --passwordenv BW_PASSWORD --raw) 

# Loop over all .json files in this directory
for json_file in *.json; do    
    echo "Processing: $json_file"
    
    # Extract item name from filename (remove .json extension)
    item_name=$(cat $json_file | jq -r .name) 
    
    # Try to get existing item, if it exists update it, otherwise create new
    existing_item=$(bw get item "$item_name" --session "$BW_SESSION" 2>/dev/null)
    if [ -n "$existing_item" ]; then
        echo "Item '$item_name' exists, updating..."
        item_id=$(echo "$existing_item" | jq -r .id)
        cat "$json_file" | bw encode | bw edit item "$item_id" --session "$BW_SESSION"
    else
        echo "Item '$item_name' does not exist, creating..."
        cat "$json_file" | bw encode | bw create item --session "$BW_SESSION"
    fi
done

bw sync --session "$BW_SESSION" # Sync Bitwarden to ensure all changes are saved

#relock the vault
bw lock
