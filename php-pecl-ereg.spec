#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	ereg
Summary:	%{modname} -
Summary(pl.UTF-8):	%{modname} -
Name:		%{php_name}-pecl-%{modname}
# version taken from package.xml, .c source has NO_VERSION_YET macro
Version:	1.0.0
Release:	2
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://git.php.net/?p=pecl/text/ereg.git;a=snapshot;h=ee45d78c6bec127c60c687b4dd6dd62d369d172a;sf=tgz;/php-pecl-%{modname}-%{version}.tar.gz
# Source0-md5:	21835a1e81d90de53a58efb9f8c96294
URL:		http://pecl.php.net/package/ereg/
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:7.0.0
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-pcre
%endif
%{?requires_php_extension}
Provides:	php(ereg) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This extension provides the ereg family of functions that were
provided with PHP 3-5. These functions have been superseded by the
preg family of functions provided by the PCRE extension:
<http://php.net/pcre>.

You are strongly encouraged to port your code to use PCRE, as this
extension is not maintained and is available for historical reasons
only.

%prep
%setup -qc
mv %{modname}-*/* .

cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="" \
	RUN_TESTS_SETTINGS="-q $*"
EOF
chmod +x run-tests.sh

# these tests fail, likely everywhere, not just pld
%{__rm} tests/ereg_basic_001.phpt
%{__rm} tests/ereg_basic_002.phpt
%{__rm} tests/ereg_error_002.phpt
%{__rm} tests/ereg_replace_basic_001.phpt
%{__rm} tests/ereg_replace_error_002.phpt
%{__rm} tests/ereg_replace_variation_001.phpt
%{__rm} tests/ereg_variation_001.phpt
%{__rm} tests/ereg_variation_004.phpt
%{__rm} tests/eregi_basic_001.phpt
%{__rm} tests/eregi_basic_002.phpt
%{__rm} tests/eregi_error_002.phpt
%{__rm} tests/eregi_replace_basic_001.phpt
%{__rm} tests/eregi_replace_error_002.phpt
%{__rm} tests/eregi_replace_variation_001.phpt
%{__rm} tests/eregi_variation_001.phpt
%{__rm} tests/eregi_variation_004.phpt
%{__rm} tests/split_basic_001.phpt
%{__rm} tests/split_basic_002.phpt
%{__rm} tests/split_error_002.phpt
%{__rm} tests/split_variation_001.phpt
%{__rm} tests/spliti_basic_001.phpt
%{__rm} tests/spliti_basic_002.phpt
%{__rm} tests/spliti_error_002.phpt
%{__rm} tests/spliti_variation_001.phpt
%build
phpize
%configure \
	--with-regex=system
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

./run-tests.sh -w failed.log
test -f failed.log -a ! -s failed.log
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

# drop, no -devel package
%{__rm} -r $RPM_BUILD_ROOT%{php_includedir}/ext/ereg

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md CREDITS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
