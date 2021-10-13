%global srcname nap
%define version 0.1.18
%define unmangled_version 0.1.18
%if 0%{?rhel} == 7
  %define dist .el7
%else
  %define dist .el8s
%endif
%define release 1%{?dist}

Summary: Python Monitoring Plugins Library
Name: python-%{srcname}
Version: 0.1.18
Release: %{release}
Source0: python-%{srcname}-%{unmangled_version}.tar.gz
License: ASL 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/python-%{srcname}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Marian Babik <<marian.babik@cern.ch>>
Packager: Marian Babik <marian.babik@cern.ch>
Url: https://gitlab.cern.ch/etf/nap
%if 0%{?el7}
BuildRequires: python-setuptools
%endif
BuildRequires: python3-setuptools

%description
Library to help write monitoring plugins in python

%if 0%{?el7}
%package -n python2-%{srcname}
Summary: %{summary}
%{?python_provide:%python_provide python2-%{srcname}}
%description -n python2-%{srcname}
Library to help write monitoring plugins in python
%endif

%package -n python3-%{srcname}
Summary: %{summary}
Requires: python3
%{?python_provide:%python_provide python3-%{srcname}}
%description -n python3-%{srcname}
Library to help write monitoring plugins in python

%prep
%autosetup -n python-%{srcname}-%{unmangled_version}

%build
%if 0%{?el7}
python2 setup.py build
%endif
python3 setup.py build

%install
%if 0%{?el7}
python2 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
%endif
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES3

%clean
rm -rf $RPM_BUILD_ROOT

%if 0%{?el7}
%files -n python2-%{srcname} -f INSTALLED_FILES
%defattr(-,root,root)
%doc README.md
%endif

%files -n python3-%{srcname} -f INSTALLED_FILES3
%defattr(-,root,root)
%doc README.md