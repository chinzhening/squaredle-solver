#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

normalize_output() {
    # Normalize to Unix line endings and trim trailing whitespace
    tr -d '\r' | sed 's/[[:space:]]*$//'
}

show_diff() {
    echo -e "${YELLOW}---- Difference (expected vs actual) ----${NC}"
    diff --color=always <(echo "$1") <(echo "$2")
}

total=5
pass_count=0

for i in $(seq 1 $total); do
    in_file="tests/$i.in"
    out_file="tests/$i.out"

    if [[ -f "$in_file" && -f "$out_file" ]]; then
        echo -n "Test case $i/$total: "

        # Run the program with a timeout to prevent hanging
        actual_output=$(timeout 5s ./build/main "$in_file" 2>&1)
        exit_code=$?

        if [[ $exit_code -ne 0 ]]; then
            echo -e "${RED}error (exit code $exit_code)${NC}"
            echo "$actual_output"
            continue
        fi

        expected_output=$(<"$out_file")

        norm_actual=$(echo "$actual_output" | normalize_output)
        norm_expected=$(echo "$expected_output" | normalize_output)

        if [[ "$norm_actual" == "$norm_expected" ]]; then
            echo -e "${GREEN}passed!${NC}"
            ((pass_count++))
        else
            echo -e "${RED}failed.${NC}"
            show_diff "$norm_expected" "$norm_actual"
        fi
    else
        echo -e "Test case $i/$total: ${YELLOW}missing input or output file${NC}"
    fi
done

echo "-----"
echo -e "Summary: ${GREEN}${pass_count}${NC}/$total tests passed."
