#!/bin/sh
svn up
svn up www/
rsync -r tychoa@tycho.ws:/home/tychoa/new.tycho.ws/static .
