#!/bin/bash

USER=/home/intel

cd $USER
DIR=$PWD/multi_sensor_sample
if [ -d "$DIR" ]; then
        echo "Success"
else
	sudo pip3 install gdown
	gdown --folder https://drive.google.com/drive/folders/1iSEjiRlYlTbuEgTb10T76f9y6aLbtavz --output $DIR
	echo -e "\e[1;32mSuccessfully installed\e[0m"
fi

