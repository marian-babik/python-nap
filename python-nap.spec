%global srcname nap
%define version 0.1.20
%define unmangled_version 0.1.20
%if 0%{?rhel} == 7
  %define dist .el7
%else
  %define dist .el8s
%endif
%define release 1%{?dist}

Summary: Python Monitoring Plugins Library
Name: python-%{srcname}
Version: 0.1.20
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
BuildRequires: python-devel
%endif
BuildRequires: python3-setuptools
BuildRequires: python3-devel

%description
Library to help write monitoring plugins in python

%if 0%{?el7}
%package -n python2-%{srcname}
Summary: %{summary}
Obsoletes: python-nap <= %{version}
Provides: python-nap = %{version}
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
%{__python2} setup.py build
%endif
%{__python3} setup.py build

%install
%if 0%{?el7}
%py2_install
%endif
%py3_install

%clean
rm -rf $RPM_BUILD_ROOT

%if 0%{?el7}
%files -n python2-%{srcname}
%defattr(-,root,root)
%doc README.md
%{python2_sitelib}/*
%endif

%files -n python3-%{srcname}
%defattr(-,root,root)
%doc README.md
%{python3_sitelib}/*
