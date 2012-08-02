#!/bin/bash

WORDSET=$1


if [[ -z "$2" ]]; then
    ACCENT="default"
else
    ACCENT="$2"
fi

for word in `cat $WORDSET`; do
    printf "%-20s   %s\n" $word $(espeak -qx "$word" -v $ACCENT)
done
