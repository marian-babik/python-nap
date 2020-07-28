%define name python-nap
%define version 0.1.15
%define unmangled_version 0.1.15
%define unmangled_version 0.1.15
%if 0%{?rhel} == 7
  %define dist .el7
%else
  %define dist .el6
%endif
%define release 1%{?dist}

Summary: Python Monitoring Plugins Library
Name: %{name}
Version: 0.1.15
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: ASL 2.0
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Marian Babik <<marian.babik@cern.ch>>
Packager: Marian Babik <marian.babik@cern.ch>
Url: https://gitlab.cern.ch/etf/nap
BuildRequires: python-setuptools

%description

Library to help write monitoring plugins in python


%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc README.md
