# Maintainer: s-geissler <aur@stefan-geissler.net>

pkgname=openhue-gui
pkgver=0.1.0
pkgrel=1
pkgdesc="System tray GUI for Philips Hue control via openhue CLI"
arch=('any')
url="https://github.com/s-geissler/openhue-gui"
license=('MIT')
depends=(
    'python>=3.8'
    'python-pillow'
    'python-gobject'
    'libappindicator'
    'gtk3'
)
makedepends=(
    'python-build'
    'python-installer'
)
optdepends=(
    'openhue: CLI tool for Philips Hue'
)
source=("https://github.com/s-geissler/openhue-gui/archive/refs/tags/${pkgver}.tar.gz")
sha256sums=('SKIP')

build() {
    cd "${pkgname}-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${pkgname}-${pkgver}"

    # Install wheel using python installer
    python -m installer --destdir="${pkgdir}" dist/*.whl

    # Install desktop file for app menu
    install -Dm644 openhue-gui.desktop "${pkgdir}/usr/share/applications/openhue-gui.desktop"
}
