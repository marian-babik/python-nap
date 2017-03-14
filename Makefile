PKGNAME=ncgx
SPECFILE=${PKGNAME}.spec

PKGVERSION=$(shell grep -s '^Version:' $(SPECFILE) | sed -e 's/Version: *//')

sources:
	python setup.py sdist
	cp dist/*.tar.gz ${PKGNAME}-${PKGVERSION}.tar.gz

srpm: sources
	rpmbuild -bs --define "_sourcedir ${PWD}" dist/ncgx.spec

rpm: sources
	rpmbuild -ba --define "_sourcedir ${PWD}" dist/ncgx.spec
