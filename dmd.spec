#
# Conditional build:
%bcond_with	bootstrap	# bootstrap using upstream binaries
%bcond_with	dynamic		# dynamic linking with libphobos (doesn't work properly as of 2.065.0)
#
Summary:	Digital Mars D compiler
Summary(pl.UTF-8):	Digital Mars D - kompilator języka D
Name:		dmd
Version:	2.072.0
Release:	1
# Digital Mars is proprietary license (not redistributable)
License:	Boost v1.0 (D runtime, Phobos, tools), GPL v1+ or Artistic (frontend), Digital Mars (backend)
Group:		Development/Languages
Source0:	http://downloads.dlang.org/releases/2.x/%{version}/%{name}.%{version}.linux.tar.xz
# NoSource0-md5:	5928fdc2065fec9440f5d255146384ad
Source1:	https://github.com/dlang/tools/archive/v%{version}/d-tools-%{version}.tar.gz
# Source1-md5:	3244aab8bb1583c3c970d8a702dd5280
Patch0:		%{name}-system-zlib.patch
Patch1:		%{name}-opt.patch
Patch2:		%{name}-shared.patch
NoSource:	0
URL:		http://dlang.org/dmd-linux.html
BuildRequires:	curl-devel
%{!?with_bootstrap:BuildRequires:	dmd >= 2.068.2}
BuildRequires:	libstdc++-devel
BuildRequires:	zlib-devel
%if %{with dynamic}
Requires:	%{name}-libs = %{version}-%{release}
%endif
# used as linker
Requires:	gcc
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%ifarch %{ix86}
%define		model	32
%else
%define		model	64
%endif

%description
Digital Mars D compiler.

%description -l pl.UTF-8
Digital Mars D - kompilator języka D.

%package libs
Summary:	Phobos runtime library for D language
Summary(pl.UTF-8):	Biblioteka uruchomieniowa Phobos dla języka D
Group:		Libraries

%description libs
Phobos runtime library for D language.

%description libs -l pl.UTF-8
Biblioteka uruchomieniowa Phobos dla języka D.

%package static
Summary:	Phobos and D-runtime static libraries for D language
Summary(pl.UTF-8):	Biblioteki statyczne Phobos oraz D-runtime dla języka D
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description static
Phobos and D-runtime static libraries for D language.

%description static -l pl.UTF-8
Biblioteki statyczne Phobos oraz D-runtime dla języka D.

%prep
%setup -q -n dmd2 -a1
%{__mv} tools-%{version} tools

%patch0 -p1
%patch1 -p1
%{?with_dynamic:%patch2 -p1}

echo "%{version}" > src/dmd/VERSION

cp -p src/dmd/backendlicense.txt dmd-backendlicense.txt
cp -p src/dmd/readme.txt dmd-readme.txt
cp -p src/druntime/LICENSE druntime-LICENSE
cp -p src/druntime/README.md druntime-README.md

%build
%{__make} -C src/dmd -f posix.mak \
	OS=LINUX \
	TARGET_CPU=X86 \
	MODEL=%{model} \
	HOST_CC="%{__cxx}" \
	%{?with_bootstrap:HOST_DMD=$(pwd)/linux/bin%{model}/dmd} \
	CXXOPTFLAGS="%{rpmcxxflags}"

DMD=$(pwd)/src/dmd/dmd

%{__make} -C src/druntime -f posix.mak \
	OS=linux \
	MODEL=%{model} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -m%{model} -fPIC -DHAVE_UNISTD_H" \
	DMD="$DMD" \
	PIC="-fPIC"

%{__make} -C src/phobos -f posix.mak \
	OS=linux \
	MODEL=%{model} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -m%{model} -fPIC -DHAVE_UNISTD_H" \
	DMD="$DMD" \
	LIBCURL_STUB= \
	PIC="-fPIC"

%{__make} -C tools -f posix.mak \
	OS=linux \
	MODEL=%{model} \
	CC="%{__cc}" \
	DMD="$DMD -I$(pwd)/src/phobos -I$(pwd)/src/druntime/import -L-L$(pwd)/src/phobos/generated/linux/release/%{model}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_includedir}/d/dmd/phobos/etc/c,%{_libdir},%{_sysconfdir},%{_docdir}/dmd}

install -Dp src/dmd/dmd $RPM_BUILD_ROOT%{_bindir}/dmd
cp -p src/druntime/generated/linux/release/%{model}/libdruntime* $RPM_BUILD_ROOT%{_libdir}
cp -a src/phobos/generated/linux/release/%{model}/libphobos2.so* $RPM_BUILD_ROOT%{_libdir}
cp -p src/phobos/generated/linux/release/%{model}/libphobos2.a $RPM_BUILD_ROOT%{_libdir}
cp -pr src/druntime/import $RPM_BUILD_ROOT%{_includedir}/d/dmd/druntime
cp -pr src/phobos/{std,*.d} $RPM_BUILD_ROOT%{_includedir}/d/dmd/phobos
cp -p src/phobos/etc/c/*.d $RPM_BUILD_ROOT%{_includedir}/d/dmd/phobos/etc/c
install tools/generated/linux/%{model}/{ddemangle,rdmd} $RPM_BUILD_ROOT%{_bindir}
install -Dp man/man1/dmd.1 $RPM_BUILD_ROOT%{_mandir}/man1/dmd.1
install -Dp man/man5/dmd.conf.5 $RPM_BUILD_ROOT%{_mandir}/man5/dmd.conf.5

# some intermediate(?) object disliked a lot by ldconfig
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libdruntime.so.a

cat >$RPM_BUILD_ROOT%{_sysconfdir}/dmd.conf <<EOF
[Environment]
DFLAGS=-I/usr/include/d/dmd/phobos -I/usr/include/d/dmd/druntime -L-L%{_libdir} -L--no-warn-search-mismatch -L--export-dynamic
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libphobos2.so.0.72.0
%attr(755,root,root) %ghost %{_libdir}/libphobos2.so.0.72

%files
%defattr(644,root,root,755)
%doc README.TXT license.txt dmd-*.txt druntime-*
%attr(755,root,root) %{_bindir}/ddemangle
%attr(755,root,root) %{_bindir}/dmd
%attr(755,root,root) %{_bindir}/rdmd
%attr(755,root,root) %{_libdir}/libphobos2.so
%{_libdir}/libdruntime.so.o
%{_libdir}/libphobos2.so.0.72.o
%{_sysconfdir}/dmd.conf
%dir %{_includedir}/d
%{_includedir}/d/dmd
%{_mandir}/man1/dmd.1*
%{_mandir}/man5/dmd.conf.5*
%{_docdir}/dmd

%if %{with dynamic}
%files static
%defattr(644,root,root,755)
%endif
%{_libdir}/libdruntime.a
%{_libdir}/libphobos2.a
