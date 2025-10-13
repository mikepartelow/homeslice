.PHONY: fmt lint test build push info

VERSION := $(if $(VERSION),$(VERSION),$(shell date +'%Y%m%d_%H%M%S'))

APPS := $(shell /bin/ls -d */ | sed 's^/^^' | sort | grep -v pylib)

info:
	for APP in ${APPS}; do echo "doing: $${APP}" && cd $${APP} && VERSION=${VERSION} make info $@ && cd ..; done

fmt:
	for APP in ${APPS}; do echo "doing: $${APP}" && cd $${APP} && VERSION=${VERSION} make fmt $@ && cd ..; done

lint:
	for APP in ${APPS}; do echo "doing: $${APP}" && cd $${APP} && VERSION=${VERSION} make lint $@ && cd ..; done

test:
	for APP in ${APPS}; do echo "doing: $${APP}" && cd $${APP} && VERSION=${VERSION} make test $@ && cd ..; done

build:
	for APP in ${APPS}; do echo "doing: $${APP}" && cd $${APP} && VERSION=${VERSION} make build $@ && cd ..; done

push:
	for APP in ${APPS}; do echo "doing: $${APP}" && cd $${APP} && VERSION=${VERSION} make push $@ && cd ..; done
