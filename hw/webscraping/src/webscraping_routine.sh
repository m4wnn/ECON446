#!/bin/bash

pwd

for i in Playa-del-Rey_Los-Angeles_CA
do
	echo "+---------- Init $i ----------+"
	python webscraper.py $i
	echo "+------------ End ------------+"
done

