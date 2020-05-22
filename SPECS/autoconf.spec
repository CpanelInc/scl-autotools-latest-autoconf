%{?_compat_el5_build}

%{!?scl:%global scl autotools-latest}

%{?scl:%scl_package autoconf}

# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define release_prefix 5

Summary:    A GNU tool for automatically configuring source code
Name:       %{?scl_prefix}autoconf
Version:    2.69
Release:    %{release_prefix}%{?dist}.cpanel
License:    GPLv2+ and GFDL
Group:      Development/Tools
Source0:    http://ftpmirror.gnu.org/autoconf/autoconf-%{version}.tar.gz
URL:        http://www.gnu.org/software/autoconf/
BuildArch: noarch


%if ! 0%{?buildroot:1}
# HACK!  This should be truth only for RHEL5, so benefit from
# this %%if for defining (otherwise undefined) macro for this platform.
%global rhel 5
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%endif

# run "make check" by default
%bcond_with check

# m4 >= 1.4.6 is required, >= 1.4.14 is recommended;  We have 1.4.5 in rhel5,
# 1.4.13 in rhel6, so don't build for el5 yet - this requires workaround with
# probably empty 'm4' SCLized package for OK platforms, don't know what is
# proper way.
%{?scl:BuildRequires: %{scl}-runtime}
%{?scl:BuildRequires: %{scl}-m4}
BuildRequires:      scl-utils-build
BuildRequires:      help2man

%{?scl:Requires: %{scl}-runtime}
%{?scl:Requires: %{scl}-m4}
BuildRequires:   emacs

%if 0%{?fedora} >= 20 || 0%{?rhel} >= 7
BuildRequires: perl-macros
%else
BuildRequires: perl-devel
%endif

BuildRequires:      perl(Data::Dumper)
# from f19, Text::ParseWords is not the part of 'perl' package
BuildRequires:      perl(Text::ParseWords)

%if %{with check}
# For extended testsuite coverage
BuildRequires:      gcc-gfortran
%if 0%{?fedora} >= 15
BuildRequires:      erlang
%endif
%endif

Requires(post):     /sbin/install-info
Requires(preun):    /sbin/install-info

%if ! 0%{?rhel} == 5
# filter out bogus perl(Autom4te*) dependencies
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}^perl\\(Autom4te::
%global __provides_exclude %{?__provides_exclude:%__provides_exclude|}^perl\\(Autom4te::
%endif

%description
GNU's Autoconf is a tool for configuring source code and Makefiles.
Using Autoconf, programmers can create portable and configurable
packages, since the person building the package is allowed to
specify various configuration options.

You should install Autoconf if you are developing software and
would like to create shell scripts that configure your source code
packages. If you are installing Autoconf, you will also need to
install the GNU m4 package.

Note that the Autoconf package is not required for the end-user who
may be configuring software with an Autoconf-generated script;
Autoconf is only required for the generation of the scripts, not
their use.

%prep
%setup -q -n autoconf-%{version}

%build
scl enable autotools-latest - <<\EOF
%configure
# not parallel safe
make
EOF

%check
%if %{with check}
scl enable autotools-latest - <<\EOF
make check # TESTSUITEFLAGS='1-198 200-' # will disable nr. 199.
EOF
%endif

%install
%if 0%{?rhel} == 5
rm -rf %{buildroot}
%endif
scl enable autotools-latest - <<\EOF
make install DESTDIR=%{buildroot}
EOF
mkdir -p %{buildroot}/share

# Don't %%exclude this in %%files as it is not generated on RHEL7
rm -rf %{buildroot}%{_infodir}/dir

%post
/sbin/install-info %{_infodir}/autoconf.info %{_infodir}/dir || :

%preun
if [ "$1" = 0 ]; then
    /sbin/install-info --del %{_infodir}/autoconf.info %{_infodir}/dir || :
fi

%files
%{_bindir}/*
%{_infodir}/autoconf.info*
# don't include standards.info, because it comes from binutils...
%exclude %{_infodir}/standards*
# don't include info's TOP directory
%{_datadir}/autoconf/
%dir %{_datadir}/emacs/
%{_datadir}/emacs/site-lisp/
%{_mandir}/man1/*
%doc AUTHORS COPYING* ChangeLog NEWS README THANKS TODO

%changelog
* Fri May 22 2020 Julian Brown <julian.brown@cpanel.net> - 2.69-5
- ZC-6865: Fix for C8

* Wed Aug 12 2015 Pavel Raiskup <praiskup@redhat.com> - 2.69-4
- use _compat_el5_build only if defined (rhbz#1252751)

* Thu May 29 2014 Pavel Raiskup <praiskup@redhat.com> - 2.69-3
- release bump for %%_compat_el5_build

* Tue Mar 25 2014 Pavel Raiskup <praiskup@redhat.com> - 2.69-2
- require the SCL-ized m4 so we may run on RHEL5

* Fri Mar 21 2014 Pavel Raiskup <praiskup@redhat.com> - 2.69-1
- copy SCL-ized spec from autotools-git repo
