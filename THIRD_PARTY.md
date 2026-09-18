# Third-party components and license scope

The skill's code and documentation are licensed under [MIT](LICENSE). This does not relicense third-party components.

This source package contains no vendored Three.js, Playwright, sharp, browser, Python, or Node distribution. Python helpers import the standard library and local modules; Node helpers use built-ins and resolve separately installed optional libraries.

| Optional library | Upstream license reviewed | Bundled here |
| --- | --- | --- |
| [Three.js](https://raw.githubusercontent.com/mrdoob/three.js/dev/LICENSE) | MIT | No |
| [Playwright](https://raw.githubusercontent.com/microsoft/playwright/main/LICENSE) | Apache-2.0 | No |
| [sharp](https://raw.githubusercontent.com/lovell/sharp/main/LICENSE) | Apache-2.0 | No |

Review date: 2026-09-16. Links above are upstream branch files, not a certification of every historical or future version. This package does not lock a third-party application environment.

The current use of separately installed libraries does not require changing the skill's own MIT license. Third-party copyright, license and NOTICE requirements remain applicable to those components. If a later release copies source, vendors node_modules, bundles a browser or ships native binaries, review the exact versions and transitive dependencies and include their required notices. In particular, sharp installations can include libvips binaries; do not treat the entire native dependency tree as Apache-2.0 merely because sharp is. See [sharp installation documentation](https://sharp.pixelplumbing.com/install/).

V2Fun wordmark and square logo assets were supplied by the project owner for brand presentation; see assets/README.md. No third-party model, font, video or audio asset is bundled. Generated projects and added showcase assets need their own dependency and rights review.

The MIT license covers this repository's software and documentation, not V2Fun service access, account credits, reference-material rights, or generated-asset usage rights. Those remain governed by their applicable terms and rights.
