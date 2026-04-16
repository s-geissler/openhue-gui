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
    'gir1.2-appindicator3-0.1'
    'gtk3'
)
makedepends=(
    'python-build'
    'python-installer'
)
optdepends=(
    'openhue: CLI tool for Philips Hue'
)
source=("https://github.com/s-geissler/openhue-gui/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('SKIP')

build() {
    cd "${pkgname}-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${pkgname}-${pkgver}"
    python -m installer --destdir="${pkgdir}" dist/*.whl

    # Install icon
    install -Dm644 icons/tray-icon.png "${pkgdir}/usr/share/icons/hicolor/64x64/apps/openhue-gui.png"
    update-icon-caches ${pkgdir}/usr/share/icons/hicolor 2>/dev/null || true

    # Install desktop file
    install -Dm644 openhue-gui.desktop "${pkgdir}/usr/share/applications/openhue-gui.desktop"
}
