# Generated by rust2rpm
%bcond_without check

###
# Cherry-pick some rust-packaging macros (from rust2rpm),
# as the package is heavily entangled in modern py3 dependencies.
# Source is at https://pagure.io/fedora-rust/rust2rpm/blob/master/f/data.
# This section can be dropped on a buildroot where "rust-packaging" rpm
# exists.

%define rust_arches x86_64 i686 armv7hl aarch64 ppc64 ppc64le s390x
%define __rustc %{_bindir}/rustc
%define __rustdoc %{_bindir}/rustdoc
%define __global_rustflags -Copt-level=3 -Cdebuginfo=2 -Clink-arg=-Wl,-z,relro,-z,now
%define __cargo %{_bindir}/cargo
%define __cargo_common_opts %{?_smp_mflags}
%define __global_rustflags_toml [%{lua:
    for arg in string.gmatch(rpm.expand("%{__global_rustflags}"), "%S+") do
        print('"' .. arg .. '", ')
    end}]

%define cargo_prep (\
set -eu \
%{__mkdir} -p .cargo \
%{__cat} > .cargo/config << EOF \
[build]\
rustc = "%{__rustc}"\
rustdoc = "%{__rustdoc}"\
rustflags = %{__global_rustflags_toml}\
\
[term]\
verbose = true\
\
[source]\
\
[source.local-registry]\
directory = "%{cargo_registry}"\
\
[source.crates-io]\
registry = "https://crates.io"\
replace-with = "local-registry"\
EOF\
%{__rm} -f Cargo.lock \
%if ! %{with check} \
# https://github.com/rust-lang/cargo/issues/3732 \
%{__awk} -i inplace -v INPLACE_SUFFIX=.orig '/^\\\[dev-dependencies/{f=1;next} /^\\\[/{f=0}; !f' Cargo.toml \
%endif \
)

###

%global crate coreos-metadata
%global cargo_registry ./vendor

Name:           rust-%{crate}
Version:        3.0.0
Release:        1%{?dist}
Summary:        A simple cloud-provider metadata agent

License:        ASL 2.0
URL:            https://github.com/coreos/coreos-metadata
Source0:        https://crates.io/api/v1/crates/%{crate}/%{version}/download#/%{crate}-%{version}.crate
Source1:        https://users.developer.core-os.net/lucab/rhcos/cargo-vendor/%{name}-%{version}-vendor.tar.xz

ExclusiveArch:  %{rust_arches}

#BuildRequires:  rust-packaging
BuildRequires:  rust
BuildRequires:  cargo
BuildRequires:  openssl-devel
BuildRequires:  systemd

%description
%{summary}.

%package -n %{crate}
Summary:        %{summary}
Requires:       openssl

%description -n %{crate}
%{summary}.

%prep
%setup -q -a 1 -n %{crate}-%{version}
%cargo_prep

%build
## This below is equivalent to:
# %cargo_build
%{__cargo} build         \
  %{__cargo_common_opts} \
  --release              \

%install
mkdir -p %{buildroot}%{_unitdir}
install -p -m 0644 -D -t %{buildroot}%{_unitdir} systemd/coreos-metadata.service
## This below is equivalent to:
# %cargo_install
%{__cargo} install              \
  %{__cargo_common_opts}        \
  --path .                      \
  --root %{buildroot}%{_prefix}
%{__rm} -f %{buildroot}%{_prefix}/.crates.toml

%if %{with check}
%check
## This below is equivalent to:
# %cargo_check
%{__cargo} test          \
  %{__cargo_common_opts} \
  --release              \
  --no-fail-fast
%endif

%files -n %{crate}
%license LICENSE
%doc README.md
%{_bindir}/coreos-metadata
%{_unitdir}/coreos-metadata.service

%changelog
* Mon Aug 27 2018 Luca Bruno <lucab@redhat.com> - 3.0.0-1
- Initial package
