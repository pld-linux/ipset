#
# TODO:
#	- -devel subpackage
#	- Requires and BuildRequires with proper versions
#
Summary:	IP sets utility
Name:		ipset
%define version_base 2.2.6
%define version_tstamp 20051028
Version:	%{version_base}_%{version_tstamp}
Release:	0.1
License:	GPL
Group:		Networking/Admin
Source0:	http://ipset.netfilter.org/%{name}-%{version_base}-%{version_tstamp}.tar.bz2
# Source0-md5:	f44ed0ddb714060716677838cd19045c
Patch0:		%{name}-no_kernel_headers.patch
URL:		http://ipset.netfilter.org/
BuildRequires:	linux-libc-headers >= 2.6.11.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# not all set types are supported by our kernel and linux-libc-headers
%define _settypes ipmap portmap macipmap iphash nethash iptree

%description
IP sets are a framework inside the Linux 2.4.x and 2.6.x kernel, which
can be administered by the ipset utility. Depending on the type,
currently an IP set may store IP addresses, (TCP/UDP) port numbers or
IP addresses with MAC addresses in a way, which ensures lightning
speed when matching an entry against a set.

%prep
%setup -qn %{name}-%{version_base}
%patch0 -p1

%build
%{__make} \
	PREFIX="%{_prefix}" \
	LIBDIR="%{_libdir}" \
	MANDIR="%{_mandir}" \
	BINDIR="%{_sbindir}" \
	SETTYPES:="%{_settypes}" \
	COPT_FLAGS:="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR="$RPM_BUILD_ROOT" \
	PREFIX="%{_prefix}" \
	LIBDIR="%{_libdir}" \
	MANDIR="%{_mandir}" \
	BINDIR="%{_sbindir}" \
	SETTYPES:="%{_settypes}"

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc ChangeLog ChangeLog.ippool TODO
%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/ipset
%attr(755,root,root) %{_libdir}/ipset/*.so
%{_mandir}/man8/*
