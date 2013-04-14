Summary:	Digital Mars D compiler
Summary(pl.UTF-8):	Digital Mars D - kompilator języka D
Name:		dmd
Version:	2.062
Release:	1
# Digital Mars is proprietary license (not redistributable)
License:	Boost (D runtime, Phobos), GPL v1+ or Artistic (compiler frontend), Digital Mars (the rest)
Group:		Development/Languages
Source0:	http://downloads.dlang.org.s3-website-us-east-1.amazonaws.com/releases/2013/%{name}.%{version}.zip
# NoSource0-md5:	fd2211206532ab41a8aef764a9225d3c
NoSource:	0
URL:		http://dlang.org/dmd-linux.html
BuildRequires:	libstdc++-devel
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

%prep
%setup -q -n dmd2

echo "%{version}" > src/VERSION

cp -p src/dmd/backendlicense.txt dmd-backendlicense.txt
cp -p src/dmd/readme.txt dmd-readme.txt
cp -p src/druntime/LICENSE druntime-LICENSE
cp -p src/druntime/README druntime-README

%build
%{__make} -C src/dmd -f posix.mak \
	OS=LINUX \
	TARGET_CPU=X86 \
	MODEL=%{model} \
	HOST_CC="%{__cxx}" \
	GFLAGS='%{rpmcxxflags} $(WARNINGS) -D__pascal= -fno-exceptions'

DMD=$(pwd)/src/dmd/dmd
%{__make} -C src/druntime -f posix.mak \
	OS=linux \
	MODEL=%{model} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -m%{model} -fPIC" \
	DMD="$DMD" \
	PIC="-fPIC"

%{__make} -C src/phobos -f posix.mak \
	OS=linux \
	MODEL=%{model} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -m%{model} -fPIC" \
	DMD="$DMD" \
	PIC="-fPIC"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_includedir}/d/dmd/phobos,%{_libdir},%{_sysconfdir},%{_docdir}/dmd}

install -Dp src/dmd/dmd $RPM_BUILD_ROOT%{_bindir}/dmd
cp -p src/druntime/lib/libdruntime-linux%{model}.a $RPM_BUILD_ROOT%{_libdir}
cp -p src/phobos/generated/linux/release/%{model}/libphobos2.a $RPM_BUILD_ROOT%{_libdir}
cp -pr src/druntime/import $RPM_BUILD_ROOT%{_includedir}/d/dmd/druntime
cp -pr src/phobos/{std,*.d} $RPM_BUILD_ROOT%{_includedir}/d/dmd/phobos
cp -pr src/druntime/doc $RPM_BUILD_ROOT%{_docdir}/dmd/druntime
install -Dp man/man1/dmd.1 $RPM_BUILD_ROOT%{_mandir}/man1/dmd.1
install -Dp man/man1/dmd.conf.5 $RPM_BUILD_ROOT%{_mandir}/man5/dmd.conf.5

cat >$RPM_BUILD_ROOT%{_sysconfdir}/dmd.conf <<EOF
[Environment]
DFLAGS=-I/usr/include/d/dmd/phobos -I/usr/include/d/dmd/druntime -L-L%{_libdir} -L--no-warn-search-mismatch -L--export-dynamic
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.TXT license.txt dmd-*.txt druntime-*
%attr(755,root,root) %{_bindir}/dmd
%{_libdir}/libdruntime-linux%{model}.a
%{_libdir}/libphobos2.a
%{_sysconfdir}/dmd.conf
%dir %{_includedir}/d
%{_includedir}/d/dmd
%{_mandir}/man1/dmd.1*
%{_mandir}/man5/dmd.conf.5*
%{_docdir}/dmd
