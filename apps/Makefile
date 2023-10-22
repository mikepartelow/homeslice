.PHONY: build push

APPS := buttons clocktime switches

build:
	for APP in ${APPS}; do cd $${APP} && make $@ && cd ..; done

push:
	for APP in ${APPS}; do cd $${APP} && make $@ && cd ..; done
