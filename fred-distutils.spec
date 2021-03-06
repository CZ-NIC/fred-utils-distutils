%define name fred-distutils
# values for 'version' and 'unmangled_version' must be provided from outside
%define release 1
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define debug_package %{nil}

Summary: Fred Distutils
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv3+
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: CZ.NIC <fred@nic.cz>
Url: https://fred.nic.cz/
BuildRequires: python
Requires: python gettext

%description
Fred Distutils, utilities for easier way to build packages.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -cO2 --force --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --prefix=/usr --install-sysconf=/etc --install-localstate=/var --no-check-deps

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
