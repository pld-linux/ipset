#
# TODO:
#	- patch our kernel to provide the needed API and update
#	  the dependencies here
#
# Conditional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)

# The goal here is to have main, userspace, package built once with
# simple release number, and only rebuild kernel packages with kernel
# version as part of release number, without the need to bump release
# with every kernel change.
%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	2
%define		pname	ipset
Summary:	IP sets utility
Summary(pl.UTF-8):	Narzędzie do zarządzania zbiorami IP
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	6.24
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	GPL v2
Group:		Networking/Admin
#Source0Download: http://ipset.netfilter.org/install.html
Source0:	http://ipset.netfilter.org/%{pname}-%{version}.tar.bz2
# Source0-md5:	8831b8f01458bf2abacc222884195a62
Source1:	%{pname}.init
Patch0:		list_last_entry.patch
URL:		http://ipset.netfilter.org/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
BuildRequires:	libmnl-devel >= 1
BuildRequires:	libltdl-devel >= 2:2.0
BuildRequires:	libtool >= 2:2.0
%{?with_userspace:BuildRequires:	linux-libc-headers >= 7:2.6.38.6}
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.701
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2}}
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

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-net-ipset\
Summary:	IPset kernel modules\
Summary(pl.UTF-8):	Moduły jądra oferujące wsparcie dla zbiorów IP\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-net-ipset\
IP sets are a framework inside the Linux 2.4.x and 2.6.x kernel, which\
can be administered by the ipset utility. Depending on the type,\
currently an IP set may store IP addresses, (TCP/UDP) port numbers or\
IP addresses with MAC addresses in a way, which ensures lightning\
speed when matching an entry against a set.\
\
This package contains kernel modules.\
\
%description -n kernel%{_alt_kernel}-net-ipset -l pl.UTF-8\
Zbiory IP to szkielet w jądrze Linuksa 2.4.x i 2.6.x, którym można\
administrować przy użyciu narzędzia ipset. W zależności od\
rodzaju aktualnie zbiór IP może przechowywać adresy IP, numery\
portów (TCP/UDP) lub adresy IP z adresami MAC - w sposób\
zapewniający maksymalną szybkość przy dopasowywaniu elementu do\
zbioru.\
\
Ten pakiet zawiera moduły jądra oferujące wsparcie dla zbiorów IP.\
\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-net-ipset\
%defattr(644,root,root,755)\
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/xt_*.ko*\
%dir /lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipset\
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipset/ip_set.ko*\
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipset/ip_set_*.ko*\
%endif\
\
%post	-n kernel%{_alt_kernel}-net-ipset\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-net-ipset\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%configure \\\
	--disable-silent-rules \\\
	--with-kmod=yes \\\
	--with-kbuild=%{_kernelsrcdir} \\\
	--with-settype-modules-list=all\
\
# a hack not to list all modules: list only ip_set, all other are build anyway\
%build_kernel_modules -C kernel/net/netfilter -m ipset/ip_set IP_SET_MAX=255 KDIR=$PWD/../..\
\
for drv in kernel/net/netfilter/ipset/ip_set*.ko ; do\
%install_kernel_modules -D installed -m ${drv%.ko} -d kernel/net/ipv4/netfilter/ipset\
done\
for drv in kernel/net/netfilter/xt_*.ko ; do\
%install_kernel_modules -D installed -m ${drv%.ko} -d kernel/net/ipv4/netfilter\
done\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1

%build
%if %{with userspace}
%configure \
	--disable-silent-rules \
	--with-kmod=no \
	--with-settype-modules-list=all

%{__make}
%endif

%{?with_kernel:%{expand:%build_kernel_packages}}

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
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post init
/sbin/chkconfig --add %{pname}

%preun init
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del %{pname}
fi

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
%{_pkgconfigdir}/libipset.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libipset.a

%files init
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/ipset
%endif
