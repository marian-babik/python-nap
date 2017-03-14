PKGNAME=python-nap
SPECFILE=${PKGNAME}.spec

PKGVERSION=$(shell grep -s '^Version:' $(SPECFILE) | sed -e 's/Version: *//')
FILES=LICENSE README.md setup.py setup.cfg MANIFEST.in nap

sources:
	rm -rf dist
	mkdir -p dist/${PKGNAME}-${PKGVERSION}
	cp -pr ${FILES} dist/${PKGNAME}-${PKGVERSION}/.
	find dist -type d -name .svn | xargs -i rm -rf {}
	find dist -type d -name .git | xargs -i rm -rf {}
	cd dist ; tar cfz ../${PKGNAME}-${PKGVERSION}.tar.gz ${PKGNAME}-${PKGVERSION}
	rm -rf dist

srpm: sources
	rpmbuild -bs --define "_sourcedir ${PWD}" dist/python-nap.spec

rpm: sources
	rpmbuild -ba --define "_sourcedir ${PWD}" dist/python-nap.spec
