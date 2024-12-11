#
# Conditional build:
%bcond_with	bootstrap	# bootstrap using upstream binaries
%bcond_without	dynamic		# dynamic linking with libphobos (static doesn't work properly as of 2.109.1)
#
Summary:	Digital Mars D compiler
Summary(pl.UTF-8):	Digital Mars D - kompilator języka D
Name:		dmd
Version:	2.109.1
Release:	1
License:	Boost v1.0
Group:		Development/Languages
Source0:	http://downloads.dlang.org/releases/2.x/%{version}/%{name}.%{version}.linux.tar.xz
# Source0-md5:	4ac0c77e283fb5b14da94e187532ba12
Source1:	https://github.com/dlang/tools/archive/v%{version}/d-tools-%{version}.tar.gz
# Source1-md5:	c32c0dc33c7a3b16e631cc9dd6b08f34
Patch0:		%{name}-system-zlib.patch
Patch2:		%{name}-shared.patch
Patch3:		%{name}-make.patch
URL:		https://dlang.org/dmd-linux.html
BuildRequires:	curl-devel
%{!?with_bootstrap:BuildRequires:	dmd >= 2.095.0}
BuildRequires:	libstdc++-devel
BuildRequires:	zlib-devel
%if %{with dynamic}
Requires:	%{name}-libs = %{version}-%{release}
%endif
# used as linker
Requires:	gcc
%if %{without dynamic}
Requires:	zlib-devel
%endif
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_debugsource_packages	%{nil}

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
%{?with_dynamic:%patch2 -p1}
%patch3 -p1

# for DMD
echo "%{version}" > VERSION
# for Phobos
echo "%{version}" > src/dmd/VERSION

cp -p src/dmd/README.md dmd-README.md
cp -p src/druntime/README.md druntime-README.md

# TODO: patch
sed -i -e 's,/compiler/src/,/dmd/,' src/druntime/Makefile
sed -i -e 's,/compiler/src/,/,' src/phobos/Makefile

%build
%if %{with bootstrap}
HOST_DMD=$(pwd)/linux/bin%{model}/dmd
HOST_RDMD=$(pwd)/linux/bin%{model}/rdmd
%else
HOST_DMD=dmd
HOST_RDMD=rdmd
%endif

cd src/dmd
$HOST_RDMD build.d -v \
	CXX="%{__cxx}" \
	CXXFLAGS="%{rpmcxxflags}" \
	ENABLE_RELEASE=1 \
	HOST_DMD="$HOST_DMD" \
	MODEL=%{model}
cd ../..

DMD=$(pwd)/generated/linux/release/%{model}/dmd

%{__make} -C src/druntime \
	OS=linux \
	MODEL=%{model} \
	DMD="$DMD" \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -m%{model} -fPIC -DHAVE_UNISTD_H" \
	PIC="-fPIC"

%{__make} -C src/phobos \
	OS=linux \
	MODEL=%{model} \
	DMD="$DMD" \
	DRUNTIME_PATH="$(pwd)/src/druntime" \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -m%{model} -fPIC -DHAVE_UNISTD_H" \
	PIC=1

%{__make} -C tools \
	OS=linux \
	MODEL=%{model} \
	CC="%{__cc}" \
	DMD="$DMD -I$(pwd)/src/phobos -I$(pwd)/src/druntime/import -L-L$(pwd)/src/phobos/generated/linux/release/%{model}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_includedir}/d/dmd/phobos/etc/c,%{_libdir},%{_sysconfdir},%{_docdir}/dmd}

install -Dp generated/linux/release/%{model}/dmd $RPM_BUILD_ROOT%{_bindir}/dmd
cp -a src/phobos/generated/linux/release/%{model}/libphobos2.so* $RPM_BUILD_ROOT%{_libdir}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libphobos2.so*.o
cp -p src/phobos/generated/linux/release/%{model}/libphobos2.a $RPM_BUILD_ROOT%{_libdir}
cp -pr src/druntime/import $RPM_BUILD_ROOT%{_includedir}/d/dmd/druntime
cp -pr src/phobos/{std,*.d} $RPM_BUILD_ROOT%{_includedir}/d/dmd/phobos
cp -p src/phobos/etc/c/*.d $RPM_BUILD_ROOT%{_includedir}/d/dmd/phobos/etc/c
install tools/generated/linux/%{model}/{ddemangle,rdmd} $RPM_BUILD_ROOT%{_bindir}
install -Dp man/man1/dmd.1 $RPM_BUILD_ROOT%{_mandir}/man1/dmd.1
install -Dp man/man5/dmd.conf.5 $RPM_BUILD_ROOT%{_mandir}/man5/dmd.conf.5

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
%attr(755,root,root) %{_libdir}/libphobos2.so.0.109.1
%attr(755,root,root) %ghost %{_libdir}/libphobos2.so.0.109

%files
%defattr(644,root,root,755)
%doc README.TXT license.txt dmd-*.md druntime-*.md
%attr(755,root,root) %{_bindir}/ddemangle
%attr(755,root,root) %{_bindir}/dmd
%attr(755,root,root) %{_bindir}/rdmd
%attr(755,root,root) %{_libdir}/libphobos2.so
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
%{_libdir}/libphobos2.a
