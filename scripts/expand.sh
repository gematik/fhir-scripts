#!/bin/bash

# Clear previous stack
fhir clear > /dev/null

cd fsh-generated/resources

# Read all ValueSets
fhir push "ValueSet-*.json"

# Initialize counters
sc=0
fl=0
cnt=1
stack=$(fhir stack)
for s in $stack; do
    echo ${cnt} ${s}
    ((cnt++))
done
echo "--"
cnt=1
# Call peek to check if there is a top element
fhir peek > /dev/null
while [ $? -eq 0 ]; do
    # Generate file name
    top=$(fhir peek)
    fileName=ValueSet-${top//ValueSet\/}.json
    echo ${cnt} ${top}
    ((cnt++))

    # Generate expansion
    # output=$(fhir expand)

    #  if [[ $? -ne 0 ]]; then
    #     # echo "❌ ${fileName} <- ${output}"
    #     ((fl++))

    #     fhir peek > /dev/null

    #     if [[ $? -ne 0 ]]; then
    #         break
    #     else
    #         continue
    #     fi
    # fi

    # Save expansion
    # output=$(fhir save $fileName --pretty)
    # outputName=${output//Resource from top of stack saved as }

    # Remove the top element
    fhir pop > /dev/null

    # Replace the previous version of the file
    # mv -f "$outputName" "$fileName"

    # echo "✅ ${fileName}"
    ((sc++))

    # Check if there is a top element left
    fhir peek > /dev/null
done

echo "Result ✅ ${sc}, ❌ ${fl}"
