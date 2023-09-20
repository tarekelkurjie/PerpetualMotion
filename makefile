SHELL := /bin/bash

make:
	@if [[ `ssh pi@172.17.21.2 test -d /home/pi/projects/$(shell basename $(CURDIR)) && echo exists` ]] ; then\
  	ssh pi@172.17.21.2 -f 'rm -rf /home/pi/projects/$(shell basename $(CURDIR))';\
	fi
	scp -pr $(CURDIR) pi@172.17.21.2:/home/pi/projects/$(shell basename $(CURDIR))/
	ssh pi@172.17.21.2 -t 'cd /home/pi/projects/$(shell basename $(CURDIR)); export DISPLAY=:0.0; python3 main.py'
