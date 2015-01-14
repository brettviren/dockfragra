#!/bin/bash

# from: http://stackoverflow.com/questions/16296753/can-you-run-gui-apps-in-a-docker-container

XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
xauth nlist :0 | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
chmod +r $XAUTH
cmd="docker run -ti -v `pwd`:/home/lbne/outland -v $XSOCK:$XSOCK -v $XAUTH:$XAUTH -e DISPLAY=$DISPLAY -e XAUTHORITY=$XAUTH upsification"
echo $cmd
$cmd
rm -f $XAUTH
