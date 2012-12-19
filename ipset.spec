#
# TODO:
#	- patch our kernel to provide the needed API and update
#	  the dependencies here
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

%define		rel	10
%define		pname	ipset
Summary:	IP sets utility
Summary(pl.UTF-8):	Narzędzie do zarządzania zbiorami IP
Name:		%{pname}%{_alt_kernel}
Version:	6.14
Release:	%{rel}
License:	GPL v2
Group:		Networking/Admin
#Source0Download: http://ipset.netfilter.org/install.html
Source0:	http://ipset.netfilter.org/%{pname}-%{version}.tar.bz2
# Source0-md5:	70f2d4c054592236dcda285855a4ee58
Source1:	%{pname}.init
Patch0:		%{pname}-no_kernel.patch
URL:		http://ipset.netfilter.org/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.38.6}
BuildRequires:	libmnl-devel >= 1
BuildRequires:	libltdl-devel
BuildRequires:	libtool >= 2:2.0
%{?with_userspace:BuildRequires:	linux-libc-headers >= 7:2.6.38.6}
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.583
Suggests:	kernel-net-ipset
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# unresolved ipset_errcode, defined in the ipset binary
%define		skip_post_check_so	libipset\.so.*

%description
IP sets are a framework inside the Linux 2.4.x and 2.6.x kernel, which
can be administered by the ipset utility. Depending on the type,
currently an IP set may store IP addresses, (TCP/UDP) port numbers or
IP addresses with MAC addresses in a way, which ensures lightning
speed when matching an entry against a set.

%description -l pl.UTF-8
Zbiory IP to szkielet w jądrze Linuksa 2.4.x i 2.6.x, którym można
administrować przy użyciu narzędzia ipset. W zależności od
rodzaju aktualnie zbiór IP może przechowywać adresy IP, numery
portów (TCP/UDP) lub adresy IP z adresami MAC - w sposób
zapewniający maksymalną szybkość przy dopasowywaniu elementu do
zbioru.

%package devel
Summary:	Header files for ipset interface
Summary(pl.UTF-8):	Pliki nagłówkowe do interfejsu ipset
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libmnl-devel >= 1

%description devel
Header files for IPset interface.

%description devel -l pl.UTF-8
Pliki nagłówkowe do interfejsu IPset.

%package static
Summary:	Static ipset interface library
Summary(pl.UTF-8):	Biblioteka statyczna interfejsu ipset
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static IPset interface library.

%description static -l pl.UTF-8
Biblioteka statyczna interfejsu IPset.

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
administrować przy użyciu narzędzia ipset. W zależności od
rodzaju aktualnie zbiór IP może przechowywać adresy IP, numery
portów (TCP/UDP) lub adresy IP z adresami MAC - w sposób
zapewniający maksymalną szybkość przy dopasowywaniu elementu do
zbioru.

Ten pakiet zawiera moduły jądra oferujące wsparcie dla zbiorów IP.

%prep
%setup -q -n %{pname}-%{version}
%{!?with_kernel:%patch0 -p1}

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	--with-kbuild=%{_kernelsrcdir}

%if %{with userspace}
%{__make}
%endif

%if %{with kernel}
# a hack not to list all modules: list only ip_set, all other are build anyway
%build_kernel_modules -C kernel/net/netfilter -m ipset/ip_set IP_SET_MAX=255 KDIR=$PWD/../..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_includedir}/libipset}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
cp include/libipset/*.h $RPM_BUILD_ROOT%{_includedir}/libipset

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{pname}
%endif

%if %{with kernel}
cd kernel/net/netfilter
%install_kernel_modules -m ipset/ip_set -d kernel/net/ipv4/netfilter/ipset
install -p ipset/ip_set_*.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipset
install -p xt_*.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter
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
%doc ChangeLog ChangeLog.ippool README UPGRADE
%attr(755,root,root) %{_sbindir}/ipset
%attr(755,root,root) %{_libdir}/libipset.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libipset.so.3
%{_mandir}/man8/ipset.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libipset.so
%{_libdir}/libipset.la
%{_includedir}/libipset

%files static
%defattr(644,root,root,755)
%{_libdir}/libipset.a

%files init
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/ipset
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-ipset
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/xt_*.ko*
%dir /lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipset
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipset/ip_set.ko*
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipset/ip_set_*.ko*
%endif
