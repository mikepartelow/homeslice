.PHONY: test build push

APPS := buttons clocktime switches

test:
	for APP in ${APPS}; do cd $${APP} && make test $@ && cd ..; done

build:
	for APP in ${APPS}; do cd $${APP} && make build $@ && cd ..; done

push:
	for APP in ${APPS}; do cd $${APP} && make push $@ && cd ..; done
