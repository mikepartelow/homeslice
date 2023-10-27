.PHONY: fmt lint test build push

APPS := buttons clocktime switches backup-todoist chime

fmt:
	for APP in ${APPS}; do cd $${APP} && make fmt $@ && cd ..; done

lint:
	for APP in ${APPS}; do cd $${APP} && make lint $@ && cd ..; done

test:
	for APP in ${APPS}; do cd $${APP} && make test $@ && cd ..; done

build:
	for APP in ${APPS}; do cd $${APP} && make build $@ && cd ..; done

push:
	for APP in ${APPS}; do cd $${APP} && make push $@ && cd ..; done
