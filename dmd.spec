Summary:	Digital Mars D compiler
Summary(pl.UTF-8):	Digital Mars D - kompilator języka D
Name:		dmd
Version:	2.065.0
Release:	1
# Digital Mars is proprietary license (not redistributable)
License:	Boost v1.0 (D runtime, Phobos), GPL v1+ or Artistic (compiler frontend), Digital Mars (the rest)
Group:		Development/Languages
Source0:	http://downloads.dlang.org/releases/2014/%{name}.%{version}.zip
# NoSource0-md5:	a17a699a7e4715658393819e9dc1814a
Patch0:		%{name}-system-zlib.patch
Patch1:		%{name}-shared.patch
NoSource:	0
URL:		http://dlang.org/dmd-linux.html
BuildRequires:	curl-devel
BuildRequires:	libstdc++-devel
BuildRequires:	zlib-devel
Requires:	%{name}-libs = %{version}-%{release}
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
%setup -q -n dmd2
%patch0 -p1
%patch1 -p1

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
	GFLAGS='%{rpmcxxflags} $(WARNINGS) -D__pascal= -fno-exceptions'

DMD=$(pwd)/src/dmd/dmd
for t in target lib/libdruntime-linux%{model}.so ; do
%{__make} -C src/druntime -f posix.mak $t \
	OS=linux \
	MODEL=%{model} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -m%{model} -fPIC" \
	DMD="$DMD" \
	PIC="-fPIC"
done

%{__make} -C src/phobos -f posix.mak \
	OS=linux \
	MODEL=%{model} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -m%{model} -fPIC" \
	DMD="$DMD" \
	LIBCURL_STUB= \
	PIC="-fPIC"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_includedir}/d/dmd/phobos,%{_libdir},%{_sysconfdir},%{_docdir}/dmd}

install -Dp src/dmd/dmd $RPM_BUILD_ROOT%{_bindir}/dmd
cp -p src/druntime/lib/libdruntime-linux%{model}* $RPM_BUILD_ROOT%{_libdir}
cp -a src/phobos/generated/linux/release/%{model}/libphobos2.so* $RPM_BUILD_ROOT%{_libdir}
cp -p src/phobos/generated/linux/release/%{model}/libphobos2.a $RPM_BUILD_ROOT%{_libdir}
cp -pr src/druntime/import $RPM_BUILD_ROOT%{_includedir}/d/dmd/druntime
cp -pr src/phobos/{std,*.d} $RPM_BUILD_ROOT%{_includedir}/d/dmd/phobos
cp -pr src/druntime/doc $RPM_BUILD_ROOT%{_docdir}/dmd/druntime
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

%files
%defattr(644,root,root,755)
%doc README.TXT license.txt dmd-*.txt druntime-*
%attr(755,root,root) %{_bindir}/dmd
%attr(755,root,root) %{_libdir}/libphobos2.so
%attr(755,root,root) %{_libdir}/libdruntime-linux%{model}.so
%{_libdir}/libdruntime-linux%{model}so.a
%{_libdir}/libdruntime-linux%{model}so.o
%{_sysconfdir}/dmd.conf
%dir %{_includedir}/d
%{_includedir}/d/dmd
%{_mandir}/man1/dmd.1*
%{_mandir}/man5/dmd.conf.5*
%{_docdir}/dmd

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libphobos2.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libphobos2.so.0.65

%files static
%defattr(644,root,root,755)
%{_libdir}/libdruntime-linux%{model}.a
%{_libdir}/libdruntime-linux%{model}.o
%{_libdir}/libphobos2.a
