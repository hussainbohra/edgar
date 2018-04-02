#! /bin/bash

sudo cat `docker inspect --format='{{.LogPath}}' ${TS_CONTAINER}` | grep 'http://localhost:8888/?token=' 

