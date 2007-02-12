#
# TODO:
#	- Requires and BuildRequires with proper versions
#
Summary:	IP sets utility
Summary(pl.UTF-8):   Narzędzie do zarządzania zbiorami IP
Name:		ipset
%define		version_base	2.2.8
%define		version_tstamp	20051203
Version:	%{version_base}_%{version_tstamp}
Release:	1
License:	GPL
Group:		Networking/Admin
Source0:	http://ipset.netfilter.org/%{name}-%{version_base}-%{version_tstamp}.tar.bz2
# Source0-md5:	a638af2788ce9e41e07dbe89311c0914
Patch0:		%{name}-no_kernel_headers.patch
URL:		http://ipset.netfilter.org/
BuildRequires:	linux-libc-headers >= 7:2.6.12.0-10
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
IP sets are a framework inside the Linux 2.4.x and 2.6.x kernel, which
can be administered by the ipset utility. Depending on the type,
currently an IP set may store IP addresses, (TCP/UDP) port numbers or
IP addresses with MAC addresses in a way, which ensures lightning
speed when matching an entry against a set.

%description -l pl.UTF-8
Zbiory IP to szkielet w jądrze Linuksa 2.4.x i 2.6.x, którym można
administrować przy użyciu narzędzia ipset. W zależności od rodzaju
aktualnie zbiór IP może przechowywać adresy IP, numery portów
(TCP/UDP) lub adresy IP z adresami MAC - w sposób zapewniający
maksymalną szybkość przy dopasowywaniu elementu do zbioru.

%package devel
Summary:	Header files for ipset interface
Summary(pl.UTF-8):   Pliki nagłówkowe do interfejsu ipset
Group:		Development/Libraries

%description devel
Header files for ipset interface.

%description devel -l pl.UTF-8
Pliki nagłówkowe do interfejsu ipset.

%prep
%setup -qn %{name}-%{version_base}
%patch0 -p1

%build
%{__make} \
	PREFIX="%{_prefix}" \
	LIBDIR="%{_libdir}" \
	MANDIR="%{_mandir}" \
	BINDIR="%{_sbindir}" \
	COPT_FLAGS:="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_includedir}

%{__make} install \
	DESTDIR="$RPM_BUILD_ROOT" \
	PREFIX="%{_prefix}" \
	LIBDIR="%{_libdir}" \
	MANDIR="%{_mandir}" \
	BINDIR="%{_sbindir}"

install *.h $RPM_BUILD_ROOT%{_includedir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc ChangeLog ChangeLog.ippool TODO
%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/ipset
%attr(755,root,root) %{_libdir}/ipset/*.so
%{_mandir}/man8/*

%files devel
%defattr(644,root,root,755)
%{_includedir}/*.h
