%global _hardened_build 1

%ifarch aarch64 %{arm} x86_64 ppc %{power64}
%global have_libguestfs 1
%endif

# We can only compile the OCaml plugin on platforms which have native
# OCaml support (not bytecode).
%ifarch %{ocaml_native_compiler}
%global have_ocaml 1
%endif

# Architectures where the complete test suite must pass.
#
# On all other architectures, a simpler test suite must pass.  This
# omits any tests that run full qemu, since running qemu under TCG is
# often broken on non-x86_64 arches.
%global complete_test_arches x86_64

# If the test suite is broken on a particular architecture, document
# it as a bug and add it to this list.
%global broken_test_arches NONE

%if 0%{?rhel} == 7
# On RHEL 7, nothing in the virt stack is shipped on aarch64 and
# libguestfs was not shipped on POWER (fixed in 7.5).  We could in
# theory make all of this work by having lots more conditionals, but
# for now limit this package to x86_64 on RHEL.
ExclusiveArch:  x86_64
%endif

# If we should verify tarball signature with GPGv2.
%global verify_tarball_signature 1

# If there are patches which touch autotools files, set this to 1.
%global patches_touch_autotools %{nil}

# The source directory.
%global source_directory 1.24-stable

Name:           nbdkit
Version:        1.24.0
Release:        5%{?dist}
Summary:        NBD server

License:        BSD
URL:            https://github.com/libguestfs/nbdkit

%if 0%{?rhel} >= 8
# On RHEL 8+, we cannot build the package on i686 (no virt stack).
ExcludeArch:    i686
%endif

Source0:        http://libguestfs.org/download/nbdkit/%{source_directory}/%{name}-%{version}.tar.gz
%if 0%{verify_tarball_signature}
Source1:        http://libguestfs.org/download/nbdkit/%{source_directory}/%{name}-%{version}.tar.gz.sig
# Keyring used to verify tarball signature.
Source2:        libguestfs.keyring
%endif

# Maintainer script which helps with handling patches.
Source3:        copy-patches.sh

# Patches come from this upstream branch:
# https://github.com/libguestfs/nbdkit/tree/rhel-8.6

# Patches.
Patch0001:     0001-cache-cow-Fix-data-corruption-in-zero-and-trim-on-un.patch
Patch0002:     0002-server-CVE-2021-3716-reset-structured-replies-on-sta.patch
Patch0003:     0003-server-reset-meta-context-replies-on-starttls.patch
Patch0004:     0004-cow-Fix-for-qemu-6.1-which-requires-backing-format.patch
Patch0005:     0005-vddk-Include-VDDK-major-library-version-in-dump-plug.patch
Patch0006:     0006-vddk-Only-print-vddk_library_version-when-we-managed.patch
Patch0007:     0007-vddk-Add-support-for-VDDK-8.0.0.patch

%if 0%{patches_touch_autotools}
BuildRequires:  autoconf, automake, libtool
%endif

%ifnarch %{complete_test_arches}
BuildRequires:  autoconf, automake, libtool
%endif
BuildRequires:  gcc, gcc-c++
BuildRequires:  /usr/bin/pod2man
BuildRequires:  gnutls-devel
BuildRequires:  libselinux-devel
%if !0%{?rhel} && 0%{?have_libguestfs}
BuildRequires:  libguestfs-devel
%endif
BuildRequires:  libvirt-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  libzstd-devel
BuildRequires:  libcurl-devel
BuildRequires:  libnbd-devel >= 1.3.11
BuildRequires:  libssh-devel
BuildRequires:  e2fsprogs, e2fsprogs-devel
%if !0%{?rhel}
BuildRequires:  genisoimage
BuildRequires:  rb_libtorrent-devel
%endif
BuildRequires:  bash-completion
BuildRequires:  perl-devel
BuildRequires:  perl(ExtUtils::Embed)
%if !0%{?rhel}
BuildRequires:  python3-devel
%else
BuildRequires:  platform-python-devel
%endif
%if !0%{?rhel}
%if 0%{?have_ocaml}
# Requires OCaml 4.02.2 which contains fix for
# http://caml.inria.fr/mantis/view.php?id=6693
BuildRequires:  ocaml >= 4.02.2
BuildRequires:  ocaml-ocamldoc
%endif
BuildRequires:  ruby-devel
BuildRequires:  tcl-devel
BuildRequires:  lua-devel
%endif
%if 0%{verify_tarball_signature}
BuildRequires:  gnupg2
%endif

# Only for running the test suite:
BuildRequires:  %{_bindir}/bc
BuildRequires:  %{_bindir}/certtool
BuildRequires:  %{_bindir}/cut
BuildRequires:  expect
BuildRequires:  %{_bindir}/hexdump
BuildRequires:  %{_sbindir}/ip
BuildRequires:  jq
BuildRequires:  %{_bindir}/nbdcopy
BuildRequires:  %{_bindir}/nbdinfo
BuildRequires:  %{_bindir}/nbdsh
BuildRequires:  %{_bindir}/qemu-img
BuildRequires:  %{_bindir}/qemu-io
BuildRequires:  %{_bindir}/qemu-nbd
BuildRequires:  %{_sbindir}/sfdisk
BuildRequires:  %{_bindir}/socat
BuildRequires:  %{_sbindir}/ss
BuildRequires:  %{_bindir}/stat
BuildRequires:  %{_bindir}/ssh-keygen

# nbdkit is a metapackage pulling the server and a useful subset
# of the plugins and filters.
Requires:       nbdkit-server%{?_isa} = %{version}-%{release}
Requires:       nbdkit-basic-plugins%{?_isa} = %{version}-%{release}
Requires:       nbdkit-basic-filters%{?_isa} = %{version}-%{release}


%description
NBD is a protocol for accessing block devices (hard disks and
disk-like things) over the network.

nbdkit is a toolkit for creating NBD servers.

The key features are:

* Multithreaded NBD server written in C with good performance.

* Minimal dependencies for the basic server.

* Liberal license (BSD) allows nbdkit to be linked to proprietary
  libraries or included in proprietary code.

* Well-documented, simple plugin API with a stable ABI guarantee.
  Lets you to export "unconventional" block devices easily.

* You can write plugins in C or many other languages.

* Filters can be stacked in front of plugins to transform the output.

'%{name}' is a meta-package which pulls in the core server and a
useful subset of plugins and filters with minimal dependencies.

If you want just the server, install '%{name}-server'.

To develop plugins, install the '%{name}-devel' package and start by
reading the nbdkit(1) and nbdkit-plugin(3) manual pages.


%package server
Summary:        The %{name} server
License:        BSD


%description server
This package contains the %{name} server with no plugins or filters.


%package basic-plugins
Summary:        Basic plugins for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Provides:       %{name}-data-plugin = %{version}-%{release}
Provides:       %{name}-eval-plugin = %{version}-%{release}
Provides:       %{name}-file-plugin = %{version}-%{release}
Provides:       %{name}-floppy-plugin = %{version}-%{release}
Provides:       %{name}-full-plugin = %{version}-%{release}
Provides:       %{name}-info-plugin = %{version}-%{release}
Provides:       %{name}-memory-plugin = %{version}-%{release}
Provides:       %{name}-null-plugin = %{version}-%{release}
Provides:       %{name}-ondemand-plugin = %{version}-%{release}
Provides:       %{name}-pattern-plugin = %{version}-%{release}
Provides:       %{name}-partitioning-plugin = %{version}-%{release}
Provides:       %{name}-random-plugin = %{version}-%{release}
Provides:       %{name}-sh-plugin = %{version}-%{release}
Provides:       %{name}-sparse-random-plugin = %{version}-%{release}
Provides:       %{name}-split-plugin = %{version}-%{release}
Provides:       %{name}-streaming-plugin = %{version}-%{release}
Provides:       %{name}-zero-plugin = %{version}-%{release}


%description basic-plugins
This package contains plugins for %{name} which only depend on simple
C libraries: glibc, gnutls, libzstd.  Other plugins for nbdkit with
more complex dependencies are packaged separately.

nbdkit-data-plugin          Serve small amounts of data from the command line.

nbdkit-eval-plugin          Write a shell script plugin on the command line.

nbdkit-file-plugin          The normal file plugin for serving files.

nbdkit-floppy-plugin        Create a virtual floppy disk from a directory.

nbdkit-full-plugin          A virtual disk that returns ENOSPC errors.

nbdkit-info-plugin          Serve client and server information.

nbdkit-memory-plugin        A virtual memory plugin.

nbdkit-null-plugin          A null (bitbucket) plugin.

nbdkit-ondemand-plugin      Create filesystems on demand.

nbdkit-pattern-plugin       Fixed test pattern.

nbdkit-partitioning-plugin  Create virtual disks from partitions.

nbdkit-random-plugin        Random content plugin for testing.

nbdkit-sh-plugin            Write plugins as shell scripts or executables.

nbdkit-sparse-random-plugin Make sparse random disks.

nbdkit-split-plugin         Concatenate one or more files.

nbdkit-streaming-plugin     A streaming file serving plugin.

nbdkit-zero-plugin          Zero-length plugin for testing.


%package example-plugins
Summary:        Example plugins for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
%if !0%{?rhel}
# example4 is written in Perl.
Requires:       %{name}-perl-plugin
%endif


%description example-plugins
This package contains example plugins for %{name}.


# The plugins below have non-trivial dependencies are so are
# packaged separately.

%if !0%{?rhel}
%package cc-plugin
Summary:        Write small inline C plugins and scripts for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Requires:       gcc
Requires:       %{_bindir}/cat


%description cc-plugin
This package contains support for writing inline C plugins and scripts
for %{name}.  NOTE this is NOT the right package for writing plugins
in C, install %{name}-devel for that.
%endif


%if !0%{?rhel}
%package cdi-plugin
Summary:        Containerized Data Import plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Requires:       jq
Requires:       podman


%description cdi-plugin
This package contains Containerized Data Import support for %{name}.
%endif


%package curl-plugin
Summary:        HTTP/FTP (cURL) plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description curl-plugin
This package contains cURL (HTTP/FTP) support for %{name}.


%if !0%{?rhel} && 0%{?have_libguestfs}
%package guestfs-plugin
Summary:        libguestfs plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description guestfs-plugin
This package is a libguestfs plugin for %{name}.
%endif


%if 0%{?rhel} == 8
%package gzip-plugin
Summary:        GZip plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description gzip-plugin
This package is a gzip plugin for %{name}.
%endif


%if !0%{?rhel}
%package iso-plugin
Summary:        Virtual ISO 9660 plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Requires:       genisoimage


%description iso-plugin
This package is a virtual ISO 9660 (CD-ROM) plugin for %{name}.
%endif


%if !0%{?rhel}
%package libvirt-plugin
Summary:        Libvirt plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description libvirt-plugin
This package is a libvirt plugin for %{name}.  It lets you access
libvirt guest disks readonly.  It is implemented using the libvirt
virDomainBlockPeek API.
%endif


%package linuxdisk-plugin
Summary:        Virtual Linux disk plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
# for mke2fs
Requires:       e2fsprogs


%description linuxdisk-plugin
This package is a virtual Linux disk plugin for %{name}.


%if !0%{?rhel}
%package lua-plugin
Summary:        Lua plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description lua-plugin
This package lets you write Lua plugins for %{name}.
%endif


%package nbd-plugin
Summary:        NBD proxy / forward plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description nbd-plugin
This package lets you forward NBD connections from %{name}
to another NBD server.


%if !0%{?rhel} && 0%{?have_ocaml}
%package ocaml-plugin
Summary:        OCaml plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description ocaml-plugin
This package lets you run OCaml plugins for %{name}.

To compile OCaml plugins you will also need to install
%{name}-ocaml-plugin-devel.


%package ocaml-plugin-devel
Summary:        OCaml development environment for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Requires:       %{name}-ocaml-plugin%{?_isa} = %{version}-%{release}


%description ocaml-plugin-devel
This package lets you write OCaml plugins for %{name}.
%endif


%if !0%{?rhel}
%package perl-plugin
Summary:        Perl plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description perl-plugin
This package lets you write Perl plugins for %{name}.
%endif


%package python-plugin
Summary:        Python 3 plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description python-plugin
This package lets you write Python 3 plugins for %{name}.


%if !0%{?rhel}
%package ruby-plugin
Summary:        Ruby plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description ruby-plugin
This package lets you write Ruby plugins for %{name}.
%endif


%package ssh-plugin
Summary:        SSH plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description ssh-plugin
This package contains SSH support for %{name}.


%package tar-plugin
Summary:        Tar archive plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Requires:       tar


%description tar-plugin
This package is a tar archive plugin for %{name}.


%if !0%{?rhel}
%package tcl-plugin
Summary:        Tcl plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description tcl-plugin
This package lets you write Tcl plugins for %{name}.
%endif


%package tmpdisk-plugin
Summary:        Remote temporary filesystem disk plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
# For mkfs and mke2fs (defaults).
Requires:       util-linux, e2fsprogs
# For other filesystems.
Suggests:       xfsprogs
%if !0%{?rhel}
Suggests:       ntfsprogs, dosfstools
%endif


%description tmpdisk-plugin
This package is a remote temporary filesystem disk plugin for %{name}.


%if !0%{?rhel}
%package torrent-plugin
Summary:        BitTorrent plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description torrent-plugin
This package is a BitTorrent plugin for %{name}.
%endif


%ifarch x86_64
%package vddk-plugin
Summary:        VMware VDDK plugin for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description vddk-plugin
This package is a plugin for %{name} which connects to
VMware VDDK for accessing VMware disks and servers.
%endif


%package basic-filters
Summary:        Basic filters for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Provides:       %{name}-blocksize-filter = %{version}-%{release}
Provides:       %{name}-cache-filter = %{version}-%{release}
Provides:       %{name}-cacheextents-filter = %{version}-%{release}
Provides:       %{name}-checkwrite-filter = %{version}-%{release}
Provides:       %{name}-cow-filter = %{version}-%{release}
Provides:       %{name}-ddrescue-filter = %{version}-%{release}
Provides:       %{name}-delay-filter = %{version}-%{release}
Provides:       %{name}-error-filter = %{version}-%{release}
Provides:       %{name}-exitlast-filter = %{version}-%{release}
Provides:       %{name}-exitwhen-filter = %{version}-%{release}
Provides:       %{name}-exportname-filter = %{version}-%{release}
Provides:       %{name}-extentlist-filter = %{version}-%{release}
Provides:       %{name}-fua-filter = %{version}-%{release}
Provides:       %{name}-ip-filter = %{version}-%{release}
Provides:       %{name}-limit-filter = %{version}-%{release}
Provides:       %{name}-log-filter = %{version}-%{release}
Provides:       %{name}-nocache-filter = %{version}-%{release}
Provides:       %{name}-noextents-filter = %{version}-%{release}
Provides:       %{name}-nofilter-filter = %{version}-%{release}
Provides:       %{name}-noparallel-filter = %{version}-%{release}
Provides:       %{name}-nozero-filter = %{version}-%{release}
Provides:       %{name}-offset-filter = %{version}-%{release}
Provides:       %{name}-partition-filter = %{version}-%{release}
Provides:       %{name}-pause-filter = %{version}-%{release}
Provides:       %{name}-rate-filter = %{version}-%{release}
Provides:       %{name}-readahead-filter = %{version}-%{release}
Provides:       %{name}-retry-filter = %{version}-%{release}
Provides:       %{name}-stats-filter = %{version}-%{release}
Provides:       %{name}-swab-filter = %{version}-%{release}
Provides:       %{name}-tls-fallback-filter = %{version}-%{release}
Provides:       %{name}-truncate-filter = %{version}-%{release}


%description basic-filters
This package contains filters for %{name} which only depend on simple
C libraries: glibc, gnutls.  Other filters for nbdkit with more
complex dependencies are packaged separately.

nbdkit-blocksize-filter    Adjust block size of requests sent to plugins.

nbdkit-cache-filter        Server-side cache.

nbdkit-cacheextents-filter Cache extents.

nbdkit-checkwrite-filter   Check writes match contents of plugin.

nbdkit-cow-filter          Copy-on-write overlay for read-only plugins.

nbdkit-ddrescue-filter     Filter for serving from ddrescue dump.

nbdkit-delay-filter        Inject read and write delays.

nbdkit-error-filter        Inject errors.

nbdkit-exitlast-filter     Exit on last client connection.

nbdkit-exitwhen-filter     Exit gracefully when an event occurs.

nbdkit-exportname-filter   Adjust export names between client and plugin.

nbdkit-extentlist-filter   Place extent list over a plugin.

nbdkit-fua-filter          Modify flush behaviour in plugins.

nbdkit-ip-filter           Filter clients by IP address.

nbdkit-limit-filter        Limit nr clients that can connect concurrently.

nbdkit-log-filter          Log all transactions to a file.

nbdkit-nocache-filter      Disable cache requests in the underlying plugin.

nbdkit-noextents-filter    Disable extents in the underlying plugin.

nbdkit-nofilter-filter     Passthrough filter.

nbdkit-noparallel-filter   Serialize requests to the underlying plugin.

nbdkit-nozero-filter       Adjust handling of zero requests by plugins.

nbdkit-offset-filter       Serve an offset and range.

nbdkit-partition-filter    Serve a single partition.

nbdkit-pause-filter        Pause NBD requests.

nbdkit-rate-filter         Limit bandwidth by connection or server.

nbdkit-readahead-filter    Prefetch data when reading sequentially.

nbdkit-retry-filter        Reopen connection on error.

nbdkit-stats-filter        Display statistics about operations.

nbdkit-swab-filter         Filter for swapping byte order.

nbdkit-tls-fallback-filter TLS protection filter.

nbdkit-truncate-filter     Truncate, expand, round up or round down size.


%if !0%{?rhel}
%package ext2-filter
Summary:        ext2, ext3 and ext4 filesystem support for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}

# Remove in Fedora 34:
Provides:       %{name}-ext2-plugin = %{version}-%{release}
Obsoletes:      %{name}-ext2-plugin <= %{version}-%{release}


%description ext2-filter
This package contains ext2, ext3 and ext4 filesystem support for
%{name}.
%endif


%package gzip-filter
Summary:        GZip filter for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description gzip-filter
This package is a gzip filter for %{name}.


%package tar-filter
Summary:        Tar archive filter for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Requires:       tar


%description tar-filter
This package is a tar archive filter for %{name}.


%package xz-filter
Summary:        XZ filter for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}


%description xz-filter
This package is the xz filter for %{name}.


%package devel
Summary:        Development files and documentation for %{name}
License:        BSD

Requires:       %{name}-server%{?_isa} = %{version}-%{release}
Requires:       pkgconfig


%description devel
This package contains development files and documentation
for %{name}.  Install this package if you want to develop
plugins for %{name}.


%package bash-completion
Summary:       Bash tab-completion for %{name}
BuildArch:     noarch
Requires:      bash-completion >= 2.0
Requires:      %{name}-server = %{version}-%{release}


%description bash-completion
Install this package if you want intelligent bash tab-completion
for %{name}.


%prep
%if 0%{verify_tarball_signature}
tmphome="$(mktemp -d)"
gpgv2 --homedir "$tmphome" --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%endif
%autosetup -p1
%if 0%{patches_touch_autotools}
autoreconf -i
%endif

%ifnarch %{complete_test_arches}
# Simplify the test suite so it doesn't require qemu.
sed -i -e 's/^LIBGUESTFS_TESTS/xLIBGUESTFS_TESTS/' tests/Makefile.am
sed -i -e '/^if HAVE_GUESTFISH/,/^endif HAVE_GUESTFISH/d' tests/Makefile.am
autoreconf -i
%endif


%build
# Golang bindings are not enabled in the build since they don't
# need to be.  Most people would use them by copying the upstream
# package into their vendor/ directory.
#
# %%{__python3} expands to platform-python, so we don't depend on
# the python module (see RHBZ#1659159, RHBZ#1867964).
export PYTHON=%{__python3}
%configure \
    --with-extra='%{name}-%{version}-%{release}' \
    --disable-static \
    --disable-golang \
    --disable-rust \
%if !0%{?rhel} && 0%{?have_ocaml}
    --enable-ocaml \
%else
    --disable-ocaml \
%endif
%if 0%{?rhel}
    --disable-lua \
    --disable-perl \
    --disable-ruby \
    --disable-tcl \
    --without-ext2 \
    --without-iso \
    --without-libvirt \
%endif
%if !0%{?rhel} && 0%{?have_libguestfs}
    --with-libguestfs \
%else
    --without-libguestfs \
%endif
    --with-tls-priority=@NBDKIT,SYSTEM

# Verify that it picked the correct version of Python
# to avoid RHBZ#1404631 happening again silently.
grep '^PYTHON_VERSION = 3' Makefile

%make_build


%install
%make_install

# Delete libtool crap.
find $RPM_BUILD_ROOT -name '*.la' -delete

# If cargo happens to be installed on the machine then the
# rust plugin is built.  Delete it if this happens.
rm -f $RPM_BUILD_ROOT%{_mandir}/man3/nbdkit-rust-plugin.3*

%if 0%{?rhel} != 8
# Remove the deprecated gzip plugin (use gzip filter instead).
rm $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins/nbdkit-gzip-plugin.so
rm $RPM_BUILD_ROOT%{_mandir}/man1/nbdkit-gzip-plugin.1*
%endif

%if 0%{?rhel}
# In RHEL, remove some plugins we cannot --disable.
for f in cc cdi torrent; do
    rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins/nbdkit-$f-plugin.so
    rm -f $RPM_BUILD_ROOT%{_mandir}/man?/nbdkit-$f-plugin.*
done
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins/nbdkit-S3-plugin
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/nbdkit-S3-plugin.1*
%endif


%check
%ifnarch %{broken_test_arches}
# Workaround for broken libvirt (RHBZ#1138604).
mkdir -p $HOME/.cache/libvirt

# tests/test-captive.sh is racy especially on s390x.  We need to
# rethink this test upstream.
truncate -s 0 tests/test-captive.sh

%ifarch s390x
# Temporarily kill tests/test-cache-max-size.sh since it fails
# sometimes on s390x for unclear reasons.
truncate -s 0 tests/test-cache-max-size.sh
%endif

# Temporarily kill test-nbd-tls.sh and test-nbd-tls-psk.sh
# https://www.redhat.com/archives/libguestfs/2020-March/msg00191.html
truncate -s 0 tests/test-nbd-tls.sh tests/test-nbd-tls-psk.sh

# Kill tests/test-cc-ocaml.sh.  Requires upstream fix (commit bce54e7df25).
truncate -s 0 tests/test-cc-ocaml.sh

# Make sure we can see the debug messages (RHBZ#1230160).
export LIBGUESTFS_DEBUG=1
export LIBGUESTFS_TRACE=1

%make_build check || {
    cat tests/test-suite.log
    exit 1
  }
%endif


%if 0%{?have_ocaml}
%ldconfig_scriptlets plugin-ocaml
%endif


%files
# metapackage so empty


%files server
%doc README
%license LICENSE
%{_sbindir}/nbdkit
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/plugins
%dir %{_libdir}/%{name}/filters
%{_mandir}/man1/nbdkit.1*
%{_mandir}/man1/nbdkit-captive.1*
%{_mandir}/man1/nbdkit-client.1*
%{_mandir}/man1/nbdkit-loop.1*
%{_mandir}/man1/nbdkit-probing.1*
%{_mandir}/man1/nbdkit-protocol.1*
%{_mandir}/man1/nbdkit-service.1*
%{_mandir}/man1/nbdkit-security.1*
%{_mandir}/man1/nbdkit-tls.1*


%files basic-plugins
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-data-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-eval-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-file-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-floppy-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-full-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-info-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-memory-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-null-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-ondemand-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-partitioning-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-pattern-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-random-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-sh-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-sparse-random-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-split-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-streaming-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-zero-plugin.so
%{_mandir}/man1/nbdkit-data-plugin.1*
%{_mandir}/man1/nbdkit-eval-plugin.1*
%{_mandir}/man1/nbdkit-file-plugin.1*
%{_mandir}/man1/nbdkit-floppy-plugin.1*
%{_mandir}/man1/nbdkit-full-plugin.1*
%{_mandir}/man1/nbdkit-info-plugin.1*
%{_mandir}/man1/nbdkit-memory-plugin.1*
%{_mandir}/man1/nbdkit-null-plugin.1*
%{_mandir}/man1/nbdkit-ondemand-plugin.1*
%{_mandir}/man1/nbdkit-partitioning-plugin.1*
%{_mandir}/man1/nbdkit-pattern-plugin.1*
%{_mandir}/man1/nbdkit-random-plugin.1*
%{_mandir}/man3/nbdkit-sh-plugin.3*
%{_mandir}/man1/nbdkit-sparse-random-plugin.1*
%{_mandir}/man1/nbdkit-split-plugin.1*
%{_mandir}/man1/nbdkit-streaming-plugin.1*
%{_mandir}/man1/nbdkit-zero-plugin.1*


%files example-plugins
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-example*-plugin.so
%if !0%{?rhel}
%{_libdir}/%{name}/plugins/nbdkit-example4-plugin
%endif
%{_mandir}/man1/nbdkit-example*-plugin.1*


%if !0%{?rhel}
%files cc-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-cc-plugin.so
%{_mandir}/man3/nbdkit-cc-plugin.3*
%endif


%if !0%{?rhel}
%files cdi-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-cdi-plugin.so
%{_mandir}/man1/nbdkit-cdi-plugin.1*
%endif


%files curl-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-curl-plugin.so
%{_mandir}/man1/nbdkit-curl-plugin.1*


%if !0%{?rhel} && 0%{?have_libguestfs}
%files guestfs-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-guestfs-plugin.so
%{_mandir}/man1/nbdkit-guestfs-plugin.1*
%endif


%if 0%{?rhel} == 8
%files gzip-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-gzip-plugin.so
%{_mandir}/man1/nbdkit-gzip-plugin.1*
%endif


%if !0%{?rhel}
%files iso-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-iso-plugin.so
%{_mandir}/man1/nbdkit-iso-plugin.1*
%endif


%if !0%{?rhel}
%files libvirt-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-libvirt-plugin.so
%{_mandir}/man1/nbdkit-libvirt-plugin.1*
%endif


%files linuxdisk-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-linuxdisk-plugin.so
%{_mandir}/man1/nbdkit-linuxdisk-plugin.1*


%if !0%{?rhel}
%files lua-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-lua-plugin.so
%{_mandir}/man3/nbdkit-lua-plugin.3*
%endif


%files nbd-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-nbd-plugin.so
%{_mandir}/man1/nbdkit-nbd-plugin.1*


%if !0%{?rhel} && 0%{?have_ocaml}
%files ocaml-plugin
%doc README
%license LICENSE
%{_libdir}/libnbdkitocaml.so.*

%files ocaml-plugin-devel
%{_libdir}/libnbdkitocaml.so
%{_libdir}/ocaml/NBDKit.*
%{_mandir}/man3/nbdkit-ocaml-plugin.3*
%{_mandir}/man3/NBDKit.3*
%endif


%if !0%{?rhel}
%files perl-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-perl-plugin.so
%{_mandir}/man3/nbdkit-perl-plugin.3*
%endif


%files python-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-python-plugin.so
%{_mandir}/man3/nbdkit-python-plugin.3*


%if !0%{?rhel}
%files ruby-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-ruby-plugin.so
%{_mandir}/man3/nbdkit-ruby-plugin.3*
%endif


%files ssh-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-ssh-plugin.so
%{_mandir}/man1/nbdkit-ssh-plugin.1*


%files tar-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-tar-plugin.so
%{_mandir}/man1/nbdkit-tar-plugin.1*


%if !0%{?rhel}
%files tcl-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-tcl-plugin.so
%{_mandir}/man3/nbdkit-tcl-plugin.3*
%endif


%files tmpdisk-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-tmpdisk-plugin.so
%{_mandir}/man1/nbdkit-tmpdisk-plugin.1*


%if !0%{?rhel}
%files torrent-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-torrent-plugin.so
%{_mandir}/man1/nbdkit-torrent-plugin.1*
%endif


%ifarch x86_64
%files vddk-plugin
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-vddk-plugin.so
%{_mandir}/man1/nbdkit-vddk-plugin.1*
%endif


%files basic-filters
%doc README
%license LICENSE
%{_libdir}/%{name}/filters/nbdkit-blocksize-filter.so
%{_libdir}/%{name}/filters/nbdkit-cache-filter.so
%{_libdir}/%{name}/filters/nbdkit-cacheextents-filter.so
%{_libdir}/%{name}/filters/nbdkit-checkwrite-filter.so
%{_libdir}/%{name}/filters/nbdkit-cow-filter.so
%{_libdir}/%{name}/filters/nbdkit-ddrescue-filter.so
%{_libdir}/%{name}/filters/nbdkit-delay-filter.so
%{_libdir}/%{name}/filters/nbdkit-error-filter.so
%{_libdir}/%{name}/filters/nbdkit-exitlast-filter.so
%{_libdir}/%{name}/filters/nbdkit-exitwhen-filter.so
%{_libdir}/%{name}/filters/nbdkit-exportname-filter.so
%{_libdir}/%{name}/filters/nbdkit-extentlist-filter.so
%{_libdir}/%{name}/filters/nbdkit-fua-filter.so
%{_libdir}/%{name}/filters/nbdkit-ip-filter.so
%{_libdir}/%{name}/filters/nbdkit-limit-filter.so
%{_libdir}/%{name}/filters/nbdkit-log-filter.so
%{_libdir}/%{name}/filters/nbdkit-nocache-filter.so
%{_libdir}/%{name}/filters/nbdkit-noextents-filter.so
%{_libdir}/%{name}/filters/nbdkit-nofilter-filter.so
%{_libdir}/%{name}/filters/nbdkit-noparallel-filter.so
%{_libdir}/%{name}/filters/nbdkit-nozero-filter.so
%{_libdir}/%{name}/filters/nbdkit-offset-filter.so
%{_libdir}/%{name}/filters/nbdkit-partition-filter.so
%{_libdir}/%{name}/filters/nbdkit-pause-filter.so
%{_libdir}/%{name}/filters/nbdkit-rate-filter.so
%{_libdir}/%{name}/filters/nbdkit-readahead-filter.so
%{_libdir}/%{name}/filters/nbdkit-retry-filter.so
%{_libdir}/%{name}/filters/nbdkit-stats-filter.so
%{_libdir}/%{name}/filters/nbdkit-swab-filter.so
%{_libdir}/%{name}/filters/nbdkit-tls-fallback-filter.so
%{_libdir}/%{name}/filters/nbdkit-truncate-filter.so
%{_mandir}/man1/nbdkit-blocksize-filter.1*
%{_mandir}/man1/nbdkit-cache-filter.1*
%{_mandir}/man1/nbdkit-cacheextents-filter.1*
%{_mandir}/man1/nbdkit-checkwrite-filter.1*
%{_mandir}/man1/nbdkit-cow-filter.1*
%{_mandir}/man1/nbdkit-ddrescue-filter.1*
%{_mandir}/man1/nbdkit-delay-filter.1*
%{_mandir}/man1/nbdkit-error-filter.1*
%{_mandir}/man1/nbdkit-exitlast-filter.1*
%{_mandir}/man1/nbdkit-exitwhen-filter.1*
%{_mandir}/man1/nbdkit-exportname-filter.1*
%{_mandir}/man1/nbdkit-extentlist-filter.1*
%{_mandir}/man1/nbdkit-fua-filter.1*
%{_mandir}/man1/nbdkit-ip-filter.1*
%{_mandir}/man1/nbdkit-limit-filter.1*
%{_mandir}/man1/nbdkit-log-filter.1*
%{_mandir}/man1/nbdkit-nocache-filter.1*
%{_mandir}/man1/nbdkit-noextents-filter.1*
%{_mandir}/man1/nbdkit-nofilter-filter.1*
%{_mandir}/man1/nbdkit-noparallel-filter.1*
%{_mandir}/man1/nbdkit-nozero-filter.1*
%{_mandir}/man1/nbdkit-offset-filter.1*
%{_mandir}/man1/nbdkit-partition-filter.1*
%{_mandir}/man1/nbdkit-pause-filter.1*
%{_mandir}/man1/nbdkit-rate-filter.1*
%{_mandir}/man1/nbdkit-readahead-filter.1*
%{_mandir}/man1/nbdkit-retry-filter.1*
%{_mandir}/man1/nbdkit-stats-filter.1*
%{_mandir}/man1/nbdkit-swab-filter.1*
%{_mandir}/man1/nbdkit-tls-fallback-filter.1*
%{_mandir}/man1/nbdkit-truncate-filter.1*


%if !0%{?rhel}
%files ext2-filter
%doc README
%license LICENSE
%{_libdir}/%{name}/filters/nbdkit-ext2-filter.so
%{_mandir}/man1/nbdkit-ext2-filter.1*
%endif


%files gzip-filter
%doc README
%license LICENSE
%{_libdir}/%{name}/filters/nbdkit-gzip-filter.so
%{_mandir}/man1/nbdkit-gzip-filter.1*


%files tar-filter
%doc README
%license LICENSE
%{_libdir}/%{name}/filters/nbdkit-tar-filter.so
%{_mandir}/man1/nbdkit-tar-filter.1*


%files xz-filter
%doc README
%license LICENSE
%{_libdir}/%{name}/filters/nbdkit-xz-filter.so
%{_mandir}/man1/nbdkit-xz-filter.1*


%files devel
%doc BENCHMARKING OTHER_PLUGINS README SECURITY TODO
%license LICENSE
# Include the source of the example plugins in the documentation.
%doc plugins/example*/*.c
%if !0%{?rhel}
%doc plugins/example4/nbdkit-example4-plugin
%doc plugins/lua/example.lua
%endif
%if !0%{?rhel} && 0%{?have_ocaml}
%doc plugins/ocaml/example.ml
%endif
%if !0%{?rhel}
%doc plugins/perl/example.pl
%endif
%doc plugins/python/examples/*.py
%if !0%{?rhel}
%doc plugins/ruby/example.rb
%endif
%doc plugins/sh/example.sh
%if !0%{?rhel}
%doc plugins/tcl/example.tcl
%endif
%{_includedir}/nbdkit-common.h
%{_includedir}/nbdkit-filter.h
%{_includedir}/nbdkit-plugin.h
%{_includedir}/nbdkit-version.h
%{_includedir}/nbd-protocol.h
%{_mandir}/man3/nbdkit-filter.3*
%{_mandir}/man3/nbdkit-plugin.3*
%{_mandir}/man1/nbdkit-release-notes-1.*.1*
%{_libdir}/pkgconfig/nbdkit.pc


%files bash-completion
%license LICENSE
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/nbdkit


%changelog
* Fri Nov 18 2022 Richard W.M. Jones <rjones@redhat.com> - 1.24.0-5
- vddk: Add support for VDDK 8.0.0
  resolves: rhbz#2143907

* Wed Jan 26 2022 Richard W.M. Jones <rjones@redhat.com> - 1.24.0-4
- Fix build on RHEL 8.6 with qemu >= 6.1
  resolves: rhbz#2045945

* Mon Sep 06 2021 Richard W.M. Jones <rjones@redhat.com> - 1.24.0-3
- Fix CVE-2021-3716 NBD_OPT_STRUCTURED_REPLY injection on STARTTLS
  resolves: rhbz#1994915

* Mon Sep 06 2021 Richard W.M. Jones <rjones@redhat.com> - 1.24.0-2
- Fix data corruption in zero and trim on unaligned tail
  resolves: rhbz#1990135

* Thu Sep 2 2021 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.24.0-1.el8
- Resolves: bz#2000225
  (Rebase virt:rhel module:stream based on AV-8.6)

* Thu Jun 04 2020 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.16.2
- Resolves: bz#1810193
  (Upgrade components in virt:rhel module:stream for RHEL-8.3 release)

* Mon Apr 27 2020 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.16.2
- Resolves: bz#1810193
  (Upgrade components in virt:rhel module:stream for RHEL-8.3 release)

* Fri Jun 28 2019 Danilo de Paula <ddepaula@redhat.com> - 1.4.2-5
- Rebuild all virt packages to fix RHEL's upgrade path
- Resolves: rhbz#1695587
  (Ensure modular RPM upgrade path)

* Mon Dec 17 2018 Richard W.M. Jones <rjones@redhat.com> - 1.4.2-4
- Remove misguided LDFLAGS hack which removed server hardening.
  https://bugzilla.redhat.com/show_bug.cgi?id=1624149#c6
  resolves: rhbz#1624149

* Fri Dec 14 2018 Richard W.M. Jones <rjones@redhat.com> - 1.4.2-3
- Use platform-python
  resolves: rhbz#1659159

* Fri Aug 10 2018 Richard W.M. Jones <rjones@redhat.com> - 1.4.2-2
- Add Enhanced Python error reporting
  resolves: rhbz#1614750.
- Use copy-patches.sh script.

* Wed Aug  1 2018 Richard W.M. Jones <rjones@redhat.com> - 1.4.2-1
- New stable version 1.4.2.

* Wed Jul 25 2018 Richard W.M. Jones <rjones@redhat.com> - 1.4.1-3
- Enable VDDK plugin on x86-64 only.

* Fri Jul 20 2018 Richard W.M. Jones <rjones@redhat.com> - 1.4.1-1
- New upstream version 1.4.1.
- Small refactorings in the spec file.

* Fri Jul  6 2018 Richard W.M. Jones <rjones@redhat.com> - 1.4.0-1
- New upstream version 1.4.0.
- New plugins: random, zero.
- New bash tab completion subpackage.
- Remove unused build dependencies.

* Sun Jul  1 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.4-3
- Add all upstream patches since 1.2.4 was released.

* Tue Jun 12 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.4-2
- Add all upstream patches since 1.2.4 was released.

* Mon Jun 11 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.4-2
- Disable plugins and filters that we do not want to ship in RHEL 8.

* Sat Jun  9 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.4-1
- New stable version 1.2.4.
- Remove upstream patches.
- Enable tarball signatures.
- Add upstream patch to fix tests when guestfish not available.

* Wed Jun  6 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.3-1
- New stable version 1.2.3.
- Add patch to work around libvirt problem with relative socket paths.
- Add patch to fix the xz plugin test with recent guestfish.

* Sat Apr 21 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.2-1
- New stable version 1.2.2.

* Mon Apr  9 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.1-1
- New stable version 1.2.1.

* Fri Apr  6 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.0-1
- Move to stable branch version 1.2.0.

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.1.28-5
- Escape macros in %%changelog

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.28-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 31 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.1.28-3
- Switch to %%ldconfig_scriptlets

* Fri Jan 26 2018 Richard W.M. Jones <rjones@redhat.com> - 1.1.28-2
- Run a simplified test suite on all arches.

* Mon Jan 22 2018 Richard W.M. Jones <rjones@redhat.com> - 1.1.28-1
- New upstream version 1.1.28.
- Add two new filters to nbdkit-basic-filters.

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 1.1.27-2
- Rebuilt for switch to libxcrypt

* Sat Jan 20 2018 Richard W.M. Jones <rjones@redhat.com> - 1.1.27-1
- New upstream version 1.1.27.
- Add new subpackage nbdkit-basic-filters containing new filters.

* Thu Jan 11 2018 Richard W.M. Jones <rjones@redhat.com> - 1.1.26-2
- Rebuild against updated Ruby.

* Sat Dec 23 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.26-1
- New upstream version 1.1.26.
- Add new pkg-config file and dependency.

* Wed Dec 06 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.25-1
- New upstream version 1.1.25.

* Tue Dec 05 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.24-1
- New upstream version 1.1.24.
- Add tar plugin (new subpackage nbdkit-plugin-tar).

* Tue Dec 05 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.23-1
- New upstream version 1.1.23.
- Add example4 plugin.
- Python3 tests require libguestfs so disable on s390x.

* Sun Dec 03 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.22-1
- New upstream version 1.1.22.
- Enable tests on Fedora.

* Sat Dec 02 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.20-1
- New upstream version 1.1.20.
- Add nbdkit-split-plugin to basic plugins.

* Sat Dec 02 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.19-2
- OCaml 4.06.0 rebuild.

* Thu Nov 30 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.19-1
- New upstream version 1.1.19.
- Combine all the simple plugins in %%{name}-basic-plugins.
- Add memory and null plugins.
- Rename the example plugins subpackage.
- Use %%license instead of %%doc for license file.
- Remove patches now upstream.

* Wed Nov 29 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.18-4
- Fix Python 3 builds / RHEL macros (RHBZ#1404631).

* Tue Nov 21 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.18-3
- New upstream version 1.1.18.
- Add NBD forwarding plugin.
- Add libselinux-devel so that SELinux support is enabled in the daemon.
- Apply all patches from upstream since 1.1.18.

* Fri Oct 20 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.16-2
- New upstream version 1.1.16.
- Disable python3 plugin on RHEL/EPEL <= 7.
- Only ship on x86_64 in RHEL/EPEL <= 7.

* Wed Sep 27 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.15-1
- New upstream version 1.1.15.
- Enable TLS support.

* Fri Sep 01 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.14-1
- New upstream version 1.1.14.

* Fri Aug 25 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.13-1
- New upstream version 1.1.13.
- Remove patches which are all upstream.
- Remove grubby hack, should not be needed with modern supermin.

* Sat Aug 19 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-13
- Rebuild for OCaml 4.05.0.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jun 27 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-10
- Rebuild for OCaml 4.04.2.

* Sun Jun 04 2017 Jitka Plesnikova <jplesnik@redhat.com> - 1.1.12-9
- Perl 5.26 rebuild

* Mon May 15 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-8
- Rebuild for OCaml 4.04.1.

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Vít Ondruch <vondruch@redhat.com> - 1.1.12-6
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.4

* Fri Dec 23 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-5
- Rebuild for Python 3.6 update.

* Wed Dec 14 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-4
- Fix python3 subpackage so it really uses python3 (RHBZ#1404631).

* Sat Nov 05 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-3
- Rebuild for OCaml 4.04.0.

* Mon Oct 03 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-2
- Compile Python 2 and Python 3 versions of the plugin.

* Wed Jun 08 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-1
- New upstream version 1.1.12
- Enable Ruby plugin.
- Disable tests on Rawhide because libvirt is broken again (RHBZ#1344016).

* Wed May 25 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-10
- Add another upstream patch since 1.1.11.

* Mon May 23 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-9
- Add all patches upstream since 1.1.11 (fixes RHBZ#1336758).

* Tue May 17 2016 Jitka Plesnikova <jplesnik@redhat.com> - 1.1.11-7
- Perl 5.24 rebuild

* Wed Mar 09 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-6
- When tests fail, dump out test-suite.log so we can debug it.

* Fri Feb 05 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-5
- Don't run tests on x86, because kernel is broken there
  (https://bugzilla.redhat.com/show_bug.cgi?id=1302071)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.11-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jan 11 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-3
- Add support for newstyle NBD protocol (RHBZ#1297100).

* Sat Oct 31 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-1
- New upstream version 1.1.11.

* Thu Jul 30 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.10-3
- OCaml 4.02.3 rebuild.

* Sat Jun 20 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.10-2
- Enable libguestfs plugin on aarch64.

* Fri Jun 19 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.10-1
- New upstream version.
- Enable now working OCaml plugin (requires OCaml >= 4.02.2).

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.9-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 11 2015 Jitka Plesnikova <jplesnik@redhat.com> - 1.1.9-5
- Perl 5.22 rebuild

* Wed Jun 10 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.9-4
- Enable debugging messages when running make check.

* Sat Jun 06 2015 Jitka Plesnikova <jplesnik@redhat.com> - 1.1.9-3
- Perl 5.22 rebuild

* Tue Oct 14 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.9-2
- New upstream version 1.1.9.
- Add the streaming plugin.
- Include fix for streaming plugin in 1.1.9.

* Wed Sep 10 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.8-4
- Rebuild for updated Perl in Rawhide.
- Workaround for broken libvirt (RHBZ#1138604).

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 21 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.8-1
- New upstream version 1.1.8.
- Add support for cURL, and new nbdkit-plugin-curl package.

* Fri Jun 20 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.7-1
- New upstream version 1.1.7.
- Remove patches which are now all upstream.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Mar 06 2014 Dan Horák <dan[at]danny.cz> - 1.1.6-4
- libguestfs is available only on selected arches

* Fri Feb 21 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.6-3
- Backport some upstream patches, fixing a minor bug and adding more tests.
- Enable the tests since kernel bug is fixed.

* Sun Feb 16 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.6-1
- New upstream version 1.1.6.

* Sat Feb 15 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.5-2
- New upstream version 1.1.5.
- Enable the new Python plugin.
- Perl plugin man page moved to section 3.
- Perl now requires ExtUtils::Embed.

* Mon Feb 10 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.4-1
- New upstream version 1.1.4.
- Enable the new Perl plugin.

* Sun Aug  4 2013 Richard W.M. Jones <rjones@redhat.com> - 1.1.3-1
- New upstream version 1.1.3 which fixes some test problems.
- Disable tests because Rawhide kernel is broken (RHBZ#991808).
- Remove a single quote from description which confused emacs.
- Remove patch, now upstream.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Jul 21 2013 Richard W.M. Jones <rjones@redhat.com> - 1.1.2-3
- Fix segfault when IPv6 client is used (RHBZ#986601).

* Tue Jul 16 2013 Richard W.M. Jones <rjones@redhat.com> - 1.1.2-2
- New development version 1.1.2.
- Disable the tests on Fedora <= 18.

* Tue Jun 25 2013 Richard W.M. Jones <rjones@redhat.com> - 1.1.1-1
- New development version 1.1.1.
- Add libguestfs plugin.
- Run the test suite.

* Mon Jun 24 2013 Richard W.M. Jones <rjones@redhat.com> - 1.0.0-4
- Initial release.
