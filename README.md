# BPS Semarang Data Repository

This repository hosts public statistical data for BPS (Badan Pusat Statistik) Semarang mobile application.

## SDGs Data

**File**: `sdgs_data.json`

Contains Sustainable Development Goals (SDGs) indicators for 35 cities/regencies in Jawa Tengah:
- 29 Kabupaten (Regencies)
- 6 Kota (Cities)

### Indicators

1. **Samitasilayak** - Sanitasi Layak (Proper Sanitation)
2. **TIK Remaja** - Tingkat Buta Huruf Remaja (Youth Literacy)
3. **TIK Dewasa** - Tingkat Buta Huruf Dewasa (Adult Literacy)
4. **Akta Lahir** - Akta Kelahiran (Birth Certificates)
5. **APM** - Angka Partisipasi Murni (Net Enrollment Rate)
6. **APK** - Angka Partisipasi Kasar (Gross Enrollment Rate)

### Data Coverage

- **Sanitation, TIK**: 2019-2024
- **Birth Certificates, APM, APK**: 2022-2024

### How to Update Data

1. Edit `sdgs_data.json` with new values
2. Update `version.txt` to new version (e.g., `1.0.0` → `1.1.0`)
3. Commit and push to GitHub
4. Apps will automatically fetch new data on next launch

### Version Format

Use semantic versioning:
- `1.0.0` - Major data update
- `1.1.0` - Minor corrections
- `1.1.1` - Bug fixes/small adjustments

## Data Source

Data provided by BPS (Badan Pusat Statistik) Jawa Tengah.

## License

Public statistical data - free to use.
