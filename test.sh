#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

total=5
pass_count=0

for i in {1..5}; do
    in_file="tests/$i.in"
    out_file="tests/$i.out"

    if [[ -f "$in_file" ]]; then
        echo -n "Test case $i/$total: "

        # Compare output directly (no temp file)
        if diff <(./main.exe "$in_file") "$out_file" > /dev/null; then
            echo -e "${GREEN}passed!${NC}"
            ((pass_count++))
        else
            echo -e "${RED}failed.${NC}"
        fi
    fi
done

echo "-----"
echo -e "Summary: ${pass_count}/$total tests passed."
