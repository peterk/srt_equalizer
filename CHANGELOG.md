## [0.1.13] - 2026-10-07

### Security
- Updated the `pytest` dev dependency to `>=9.0.3` (resolves to 9.1.1) to fix [CVE-2025-71176](https://nvd.nist.gov/vuln/detail/CVE-2025-71176) / GHSA-6w46-j5rx-g56g, an insecure `/tmp/pytest-of-{user}` directory handling issue. Running the test suite now requires Python >=3.10; the published package's own Python support (`>=3.8`) is unchanged.

## [0.1.12] - 2026-01-11

### Added
- Fix splitting on quoted text to prevent splitting next to quotes in German, Spanish and French.

## [0.1.11] - 2026-01-10

### Added
- Fix splitting on quoted text to prevent splitting next to quotes.

### Acknowledgments
- Thanks to @nicorikken for the issue report.

## [0.1.10] - 2024-08-03

### Added
- New method to split long srt lines taking punctuation into account.

### Acknowledgments
- Thanks to @dudil for the new splitting method.

## [0.1.9] - 2024-03-02

### Changed
- Fix fractional timestamps from Whisper output.

## [0.1.8] - 2023-12-08

### Added
- New method to split long srt lines in the middle in order to avoid single words on the next line. 

### Acknowledgments
- Thanks to @nixie for the new splitting method.