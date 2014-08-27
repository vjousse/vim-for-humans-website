#!/bin/bash
 
export LANG='en_GB.UTF-8'
export LC_ALL='en_GB.UTF-8'

NAME="vimebook" # Name of the application
ROOTDIR=/home/vimebook/python/vim-for-humans-website
SOCKFILE=$ROOTDIR/run/gunicorn.sock # we will communicate using this unix socket
USER=vimebook # the user to run as
GROUP=vimebook # the group to run as
NUM_WORKERS=3 # how many worker processes should Gunicorn spawn
WSGI_MODULE=wsgi_prod # WSGI module name
 
echo "Starting $NAME"
 
# Activate the virtual environment
cd $ROOTDIR
source ./env/bin/activate
export PYTHONPATH=$ROOTDIR:$PYTHONPATH
 
# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
 
# Start your Flask Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ./env/bin/gunicorn ${WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--bind=0.0.0.0:8000 \
--timeout=3600
#--bind=unix:$SOCKFILE
