#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	17
%define		pname	ipset
Summary:	IP sets utility
Summary(pl.UTF-8):	Narzędzie do zarządzania zbiorami IP
Name:		%{pname}%{_alt_kernel}
Version:	4.4
Release:	%{rel}
License:	GPL
Group:		Networking/Admin
Source0:	http://ipset.netfilter.org/%{pname}-%{version}.tar.bz2
# Source0-md5:	e21e9d9dfb8a01fc0122323ff1d6cbdb
Source1:	%{pname}.init
Patch0:		shadow-args.patch
URL:		http://ipset.netfilter.org/
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
%{?with_userspace:BuildRequires:	linux-libc-headers >= 7:2.6.22.1-2}
BuildRequires:	rpmbuild(macros) >= 1.379
Suggests:	kernel-net-ipset
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
Summary(pl.UTF-8):	Pliki nagłówkowe do interfejsu ipset
Group:		Development/Libraries

%description devel
Header files for IPset interface.

%description devel -l pl.UTF-8
Pliki nagłówkowe do interfejsu IPset.

%package init
Summary:	IPset init script
Summary(pl.UTF-8):	Skrypt startowy IPset
Group:		Networking/Admin
Requires(post,preun):	/sbin/chkconfig
Requires:	%{pname} = %{version}-%{release}
Requires:	rc-scripts

%description init
IPset initialization script.

%description init -l pl.UTF-8
Skrypt startowy IPset.

%package -n kernel%{_alt_kernel}-net-ipset
Summary:	IPset kernel modules
Summary(pl.UTF-8):	Moduły jądra oferujące wsparcie dla zbiorów IP
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-net-ipset
IP sets are a framework inside the Linux 2.4.x and 2.6.x kernel, which
can be administered by the ipset utility. Depending on the type,
currently an IP set may store IP addresses, (TCP/UDP) port numbers or
IP addresses with MAC addresses in a way, which ensures lightning
speed when matching an entry against a set.

This package contains kernel modules.

%description -n kernel%{_alt_kernel}-net-ipset -l pl.UTF-8
Zbiory IP to szkielet w jądrze Linuksa 2.4.x i 2.6.x, którym można
administrować przy użyciu narzędzia ipset. W zależności od rodzaju
aktualnie zbiór IP może przechowywać adresy IP, numery portów
(TCP/UDP) lub adresy IP z adresami MAC - w sposób zapewniający
maksymalną szybkość przy dopasowywaniu elementu do zbioru.

Ten pakiet zawiera moduły jądra oferujące wsparcie dla zbiorów IP.

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1
mv kernel/{Kbuild,Makefile}

# these options can be overriden by module parameters.
# maximum number of ipsets.
%{__sed} -i 's:$(IP_NF_SET_MAX):256:' kernel/Makefile
# hash size for bindings of IP sets.
%{__sed} -i 's:$(IP_NF_SET_HASHSIZE):1024:' kernel/Makefile

%if "%{cc_version}" < "3.4"
%{__sed} -i -e 's/-Wextra//' Makefile
%{__sed} -i -e 's/-Winit-self//' Makefile
%{__sed} -i -e 's/-Wold-style-definition//' Makefile
%{__sed} -i -e 's/-Wno-missing-field-initializers//' Makefile
%endif

%build
%if %{with userspace}
%{__make} binaries \
	CC="%{__cc}" \
	PREFIX="%{_prefix}" \
	LIBDIR="%{_libdir}" \
	MANDIR="%{_mandir}" \
	BINDIR="%{_sbindir}" \
	COPT_FLAGS:="%{rpmcflags}"
%endif

%if %{with kernel}
# ugly hack for satisfy rpm build macro. in fact all modules will be built.
%build_kernel_modules -C kernel -m ip_set
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_includedir}}

%{__make} binaries_install \
	DESTDIR="$RPM_BUILD_ROOT" \
	PREFIX="%{_prefix}" \
	LIBDIR="%{_libdir}" \
	MANDIR="%{_mandir}" \
	BINDIR="%{_sbindir}"

cp -a *.h $RPM_BUILD_ROOT%{_includedir}
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{pname}
%endif

%if %{with kernel}
cd kernel
%install_kernel_modules -m ip_set -d kernel/net/ipv4/netfilter
install -p ip_set_*.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter
install -p ipt_*.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter
cd -
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post init
/sbin/chkconfig --add %{pname}

%preun init
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del %{pname}
fi

%post	-n kernel%{_alt_kernel}-net-ipset
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-ipset
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc ChangeLog ChangeLog.ippool TODO
%attr(755,root,root) %{_sbindir}/ipset
%dir %{_libdir}/ipset
%attr(755,root,root) %{_libdir}/ipset/libipset_*.so
%{_mandir}/man8/ipset.8*

%files devel
%defattr(644,root,root,755)
%{_includedir}/ipset.h
%{_includedir}/libipt_set.h

%files init
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/ipset
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-ipset
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set*.ko*
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipt_set*.ko*
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipt_SET*.ko*
%endif
