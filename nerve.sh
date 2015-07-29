#!/bin/sh

while [ 1 ]
do
	python3 nerve.py -c $1

        if [ $? -ne 42 ]
        then
            break
        fi

	sleep 1
done

