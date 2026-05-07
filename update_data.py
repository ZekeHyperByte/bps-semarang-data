#!/usr/bin/env python3
"""Data update tool for BPS Semarang Data Repository.

Usage:
  python update_data.py <category>   - Update data for a category interactively
  python update_data.py bump          - Bump version, commit & push all changes
  python update_data.py list          - List current data status
  python update_data.py validate      - Validate all JSON files

Categories: inflasi, penduduk, ipm, kemiskinan, ekonomi, pendidikan,
            tenaga_kerja, ipg, idg, sdgs
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

CATEGORIES = [
    'inflasi', 'penduduk', 'ipm', 'kemiskinan', 'ekonomi',
    'pendidikan', 'tenaga_kerja', 'ipg', 'idg', 'sdgs',
]

REPO_DIR = Path(__file__).parent

MONTHS = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]


def load_json(category):
    path = REPO_DIR / f'{category}_data.json'
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(category, data):
    path = REPO_DIR / f'{category}_data.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'Saved {category}_data.json')


def bump_version(part='patch'):
    path = REPO_DIR / 'version.txt'
    current = path.read_text().strip() if path.exists() else '0.0.0'
    parts = current.split('.')
    if len(parts) != 3:
        parts = ['0', '0', '0']
    if part == 'major':
        parts = [str(int(parts[0]) + 1), '0', '0']
    elif part == 'minor':
        parts = [parts[0], str(int(parts[1]) + 1), '0']
    else:
        parts = [parts[0], parts[1], str(int(parts[2]) + 1)]
    new_version = '.'.join(parts)
    path.write_text(new_version + '\n')
    print(f'Version bumped: {current} -> {new_version}')
    return new_version


def git_commit_push(version):
    subprocess.run(['git', 'add', '.'], cwd=REPO_DIR, check=True)
    result = subprocess.run(
        ['git', 'diff', '--cached', '--quiet'],
        cwd=REPO_DIR, capture_output=True
    )
    if result.returncode == 0:
        print('No changes to commit')
        return
    subprocess.run(
        ['git', 'commit', '-m', f'data: update to v{version}'],
        cwd=REPO_DIR, check=True
    )
    print(f'Committed v{version}')
    try:
        subprocess.run(['git', 'push'], cwd=REPO_DIR, check=True)
        print(f'Pushed v{version} to remote')
    except subprocess.CalledProcessError:
        print('Push failed - you may need to push manually: git push')


def list_status():
    print('Category data files:')
    for cat in CATEGORIES:
        path = REPO_DIR / f'{cat}_data.json'
        if path.exists():
            size = path.stat().st_size
            data = load_json(cat)
            keys = list(data.keys())[:5]
            mod_time = datetime.fromtimestamp(path.stat().st_mtime)
            print(f'  {cat}: {size:,} bytes, keys: {keys}, modified: {mod_time}')
        else:
            print(f'  {cat}: NOT FOUND')
    version_path = REPO_DIR / 'version.txt'
    if version_path.exists():
        print(f'\nVersion: {version_path.read_text().strip()}')


def validate_all():
    errors = 0
    for cat in CATEGORIES:
        path = REPO_DIR / f'{cat}_data.json'
        if not path.exists():
            print(f'  MISSING: {cat}_data.json')
            errors += 1
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f'  OK: {cat}_data.json ({len(json.dumps(data))} chars)')
        except json.JSONDecodeError as e:
            print(f'  INVALID JSON: {cat}_data.json - {e}')
            errors += 1
    version_path = REPO_DIR / 'version.txt'
    if not version_path.exists():
        print('  MISSING: version.txt')
        errors += 1
    else:
        print(f'  OK: version.txt ({version_path.read_text().strip()})')
    return errors == 0


def prompt_float(prompt, allow_null=False):
    while True:
        val = input(prompt).strip()
        if val == '' and allow_null:
            return None
        if val == 'null' and allow_null:
            return None
        try:
            return float(val)
        except ValueError:
            print('  Please enter a valid number')


def prompt_int(prompt, allow_null=False):
    while True:
        val = input(prompt).strip()
        if val == '' and allow_null:
            return None
        try:
            return int(val)
        except ValueError:
            print('  Please enter a valid integer')


def prompt_string(prompt, allow_null=False):
    val = input(prompt).strip()
    if val == '' and allow_null:
        return None
    return val


def update_inflasi():
    data = load_json('inflasi')
    if not data:
        data = {
            'monthlyInflationData': {},
            'yearlyInflation': {},
            'ihkData': {},
            'inflationComponentsMonthly': {},
            'inflationComponentsYearly': {},
        }

    year = prompt_int('Year to update: ')
    year_str = str(year)

    print(f'\n--- Monthly Inflation for {year} ---')
    print('Enter monthly inflation values (MoM %). Press Enter to skip remaining months.')
    monthly = []
    for i, month in enumerate(MONTHS):
        val = input(f'  {month}: ').strip()
        if val == '':
            break
        try:
            monthly.append(float(val))
        except ValueError:
            print(f'  Skipping invalid value for {month}')
            break
    if monthly:
        data['monthlyInflationData'][year_str] = monthly

    yearly = prompt_float(f'Yearly inflation for {year} (YoY %): ')
    if yearly is not None:
        data['yearlyInflation'][year_str] = yearly

    ihk = prompt_float(f'IHK index for {year}: ')
    if ihk is not None:
        data['ihkData'][year_str] = ihk

    print('\n--- Inflation Components ---')
    components = [
        'Makanan, Minuman & Tembakau', 'Pakaian & Alas Kaki',
        'Perumahan & Fasilitas', 'Perlengkapan Rumah Tangga',
        'Kesehatan', 'Transportasi', 'Komunikasi & Keuangan',
        'Rekreasi & Olahraga', 'Pendidikan', 'Restoran',
        'Perawatan Pribadi'
    ]

    if 'inflationComponentsMonthly' not in data:
        data['inflationComponentsMonthly'] = {}
    if 'inflationComponentsYearly' not in data:
        data['inflationComponentsYearly'] = {}

    for comp in components:
        val = input(f'\n  Yearly % for "{comp}" (Enter to skip): ').strip()
        if val == '':
            continue
        try:
            comp_yearly = float(val)
            if comp not in data['inflationComponentsYearly']:
                data['inflationComponentsYearly'][comp] = {}
            data['inflationComponentsYearly'][comp][year_str] = comp_yearly
        except ValueError:
            print(f'    Skipping invalid value')
            continue

        monthly_comp = input(f'  Add monthly data for "{comp}"? (y/N): ').strip().lower()
        if monthly_comp == 'y':
            comp_monthly = []
            for j, month in enumerate(MONTHS[:len(monthly)]):
                mv = input(f'    {month}: ').strip()
                if mv == '':
                    break
                try:
                    comp_monthly.append(float(mv))
                except ValueError:
                    break
            if comp_monthly:
                if comp not in data['inflationComponentsMonthly']:
                    data['inflationComponentsMonthly'][comp] = {}
                data['inflationComponentsMonthly'][comp][year_str] = comp_monthly

    save_json('inflasi', data)


def update_penduduk():
    data = load_json('penduduk')
    if not data:
        data = {'penduduk': {}, 'ageDistribution': {}, 'districtDensity': {}}

    year = prompt_int('Year to update: ')
    year_str = str(year)

    print(f'\n--- Population Data for {year} ---')
    pend = {}
    pend['year'] = year
    pend['population'] = prompt_int('Total population: ')
    pend['malePopulation'] = prompt_int('Male population: ')
    pend['femalePopulation'] = prompt_int('Female population: ')
    pend['area'] = prompt_float('Area (km2): ')
    pend['density'] = prompt_int('Density (per km2): ')
    pend['districts'] = prompt_int('Number of districts: ')
    pend['villages'] = prompt_int('Number of villages: ')
    pend['growthRate'] = prompt_float('Growth rate (%: ')
    data['penduduk'][year_str] = pend

    print(f'\n--- Age Distribution for {year} ---')
    age = {}
    age['usiaMuda'] = prompt_int('Usia Muda count: ')
    age['usiaMudaPercentage'] = prompt_float('Usia Muda %: ')
    age['usiaProduktif'] = prompt_int('Usia Produktif count: ')
    age['usiaProduktifPercentage'] = prompt_float('Usia Produktif %: ')
    age['usiaTua'] = prompt_int('Usia Tua count: ')
    age['usiaTuaPercentage'] = prompt_float('Usia Tua %: ')
    data['ageDistribution'][year_str] = age

    print(f'\n--- District Density for {year} (top 5) ---')
    districts = []
    for i in range(5):
        print(f'  District {i+1}:')
        name = prompt_string('    Name: ')
        if not name:
            break
        density = prompt_int('    Density: ')
        population = prompt_float('    Population (thousands): ')
        districts.append({'name': name, 'density': density, 'population': population})
    data['districtDensity'][year_str] = districts

    save_json('penduduk', data)


def update_ipm():
    data = load_json('ipm')
    if not data:
        data = {'ipmData': {}, 'komponenData': {}}

    year = prompt_int('Year to update: ')
    year_str = str(year)

    print(f'\n--- IPM Data for {year} ---')
    ipm = {}
    ipm['uhh'] = prompt_float('UHH (Umur Harapan Hidup): ')
    ipm['rls'] = prompt_float('RLS (Rata-rata Lama Sekolah): ')
    ipm['hls'] = prompt_float('HLS (Harapan Lama Sekolah): ')
    ipm['pengeluaran'] = prompt_float('Pengeluaran (ribu): ')
    ipm['ipm'] = prompt_float('IPM: ')
    data['ipmData'][year_str] = ipm

    print(f'\n--- Komponen Data for {year} ---')
    komp = {}
    komp['ipmNasional'] = prompt_float('IPM Nasional: ')
    komp['ipmJateng'] = prompt_float('IPM Jawa Tengah: ')
    komp['ipmSemarang'] = prompt_float('IPM Kota Semarang: ')
    data['komponenData'][year_str] = komp

    save_json('ipm', data)


def update_kemiskinan():
    data = load_json('kemiskinan')
    if not data:
        data = {'kemiskinanData': {}}

    year = prompt_int('Year to update: ')
    year_str = str(year)

    print(f'\n--- Kemiskinan Data for {year} ---')
    kem = {}
    kem['pendudukMiskin'] = prompt_string('Penduduk miskin (display, e.g. "79,58 Ribu"): ')
    kem['pendudukMiskinValue'] = prompt_float('Penduduk miskin (numeric): ')
    kem['persentase'] = prompt_string('Persentase (display, e.g. "4,34%"): ')
    kem['persentaseValue'] = prompt_float('Persentase (numeric): ')
    kem['garisMiskin'] = prompt_string('Garis kemiskinan (display): ')
    kem['indeksKedalaman'] = prompt_string('Indeks kedalaman: ')
    kem['indeksKeparahan'] = prompt_string('Indeks keparahan: ')
    data['kemiskinanData'][year_str] = kem

    save_json('kemiskinan', data)


def update_ekonomi():
    data = load_json('ekonomi')
    if not data:
        data = {'ekonomiData': []}

    print('\n--- Ekonomi Data ---')
    print('Existing entries:', [e.get('tahun', '?') for e in data.get('ekonomiData', [])])

    entry = {}
    entry['id'] = str(len(data.get('ekonomiData', [])))
    entry['tahun'] = prompt_string('Year: ')
    entry['pertumbuhanEkonomi'] = prompt_string('Pertumbuhan ekonomi (e.g. "6,49%"): ')
    entry['kontribusiPDRB'] = prompt_string('Kontribusi PDRB (e.g. "14,94%"): ')
    entry['sektorIndustri'] = prompt_string('Sektor industri %: ')
    entry['sektorKonstruksi'] = prompt_string('Sektor konstruksi %: ')
    entry['sektorPerdag'] = prompt_string('Sektor perdagangan %: ')
    entry['pdrbPerKapita'] = prompt_string('PDRB per kapita: ')
    entry['vsJawaTengah'] = prompt_string('vs Jawa Tengah: ')
    entry['tpt'] = prompt_string('TPT: ')

    print('\nSemarang chart data (year:value pairs, empty line to finish):')
    semarang = []
    while True:
        line = input('  Year,Value (e.g. 2025,6.49): ').strip()
        if not line:
            break
        parts = line.split(',')
        if len(parts) == 2:
            try:
                semarang.append({'year': int(parts[0]), 'value': float(parts[1])})
            except ValueError:
                print('  Invalid format')
    entry['semarangData'] = semarang

    print('\nJateng chart data (year:value pairs, empty line to finish):')
    jateng = []
    while True:
        line = input('  Year,Value (e.g. 2025,5.37): ').strip()
        if not line:
            break
        parts = line.split(',')
        if len(parts) == 2:
            try:
                jateng.append({'year': int(parts[0]), 'value': float(parts[1])})
            except ValueError:
                print('  Invalid format')
    entry['jatengData'] = jateng

    data.setdefault('ekonomiData', []).append(entry)
    save_json('ekonomi', data)


def update_pendidikan():
    data = load_json('pendidikan')
    if not data:
        data = {'pendidikanData': {}}

    year = prompt_int('Year to update: ')
    year_str = str(year)

    print(f'\n--- Pendidikan Data for {year} ---')
    ped = {}
    ped['angkaMelekHuruf'] = prompt_float('Angka melek huruf %: ')
    ped['rataRataLamaSekolah'] = prompt_float('Rata-rata lama sekolah: ')
    ped['harapanLamaSekolah'] = prompt_float('Harapan lama sekolah: ')
    ped['rasioGuruMurid'] = prompt_float('Rasio guru murid: ')

    print('\nJenjang pendidikan (empty name to finish):')
    jenjang = []
    while True:
        name = prompt_string('  Jenjang name (e.g. TK): ')
        if not name:
            break
        sekolah = prompt_int('  Jumlah sekolah: ')
        guru = prompt_int('  Jumlah guru: ')
        murid = prompt_int('  Jumlah murid: ')
        jenjang.append({'jenjang': name, 'sekolah': sekolah, 'guru': guru, 'murid': murid})
    ped['jenjangPendidikan'] = jenjang

    print('\nRasio data (empty name to finish):')
    rasio = []
    while True:
        name = prompt_string('  Jenjang name (e.g. TK/RA): ')
        if not name:
            break
        rsm = prompt_float('  Rasio sekolah murid: ')
        rgm = prompt_float('  Rasio guru murid: ')
        rasio.append({'jenjang': name, 'rasioSekolahMurid': rsm, 'rasioGuruMurid': rgm})
    ped['rasioData'] = rasio

    print('\nPartisipasi pendidikan (empty name to finish):')
    partisipasi = []
    while True:
        name = prompt_string('  Jenjang name (e.g. SD/MI): ')
        if not name:
            break
        apm = prompt_float('  APM: ')
        apk = prompt_float('  APK: ')
        partisipasi.append({'jenjang': name, 'apm': apm, 'apk': apk})
    ped['partisipasiPendidikan'] = partisipasi

    data['pendidikanData'][year_str] = ped
    save_json('pendidikan', data)


def update_tenaga_kerja():
    data = load_json('tenaga_kerja')
    if not data:
        data = {
            'pengangguranData': {}, 'yearData': {},
            'indikatorData': {}, 'distribusiData': {}, 'jatengData': {},
        }

    year = prompt_int('Year to update: ')
    year_str = str(year)

    print(f'\n--- Pengangguran Data for {year} ---')
    peng = {}
    peng['tptSemarang'] = prompt_float('TPT Semarang %: ')
    peng['tpakSemarang'] = prompt_float('TPAK Semarang %: ')
    peng['tptJateng'] = prompt_float('TPT Jateng %: ')
    peng['tpakJateng'] = prompt_float('TPAK Jateng %: ')
    data['pengangguranData'][year_str] = peng

    print(f'\n--- Year Data for {year} ---')
    yd = {}
    yd['tpt'] = prompt_float('TPT: ')
    yd['tingkatPartisipasi'] = prompt_float('Tingkat partisipasi: ')
    yd['bekerja'] = prompt_int('Bekerja: ')
    yd['pengangguran'] = prompt_int('Pengangguran: ')
    data['yearData'][year_str] = yd

    print(f'\n--- Indikator Data for {year} ---')
    ind = {}
    ind['angkatanKerja'] = prompt_int('Angkatan kerja: ')
    ind['bkbk'] = prompt_int('BKBK: ')
    ind['tingkatKesempatan'] = prompt_float('Tingkat kesempatan %: ')
    data['indikatorData'][year_str] = ind

    print(f'\n--- Distribusi Data for {year} ---')
    dist = {}
    dist['Pertanian'] = prompt_float('Pertanian %: ')
    dist['Manufaktur'] = prompt_float('Manufaktur %: ')
    dist['Jasa'] = prompt_float('Jasa %: ')
    data['distribusiData'][year_str] = dist

    print(f'\n--- Jateng Data for {year} ---')
    jtg = {}
    jtg['tpt'] = prompt_float('TPT Jateng: ')
    jtg['tingkatPartisipasi'] = prompt_float('Tingkat partisipasi Jateng: ')
    data['jatengData'][year_str] = jtg

    save_json('tenaga_kerja', data)


def update_ipg():
    data = load_json('ipg')
    if not data:
        data = {'ipgData': {}}

    year = prompt_int('Year to update: ')
    year_str = str(year)

    print(f'\n--- IPG Data for {year} ---')
    ipg = {}
    ipg['UHH_Laki'] = prompt_float('UHH Laki-laki: ', allow_null=True)
    ipg['UHH_Perempuan'] = prompt_float('UHH Perempuan: ', allow_null=True)
    ipg['HLS_Laki'] = prompt_float('HLS Laki-laki: ', allow_null=True)
    ipg['HLS_Perempuan'] = prompt_float('HLS Perempuan: ', allow_null=True)
    ipg['RLS_Laki'] = prompt_float('RLS Laki-laki: ', allow_null=True)
    ipg['RLS_Perempuan'] = prompt_float('RLS Perempuan: ', allow_null=True)
    ipg['PPP_Laki'] = prompt_float('PPP Laki-laki: ', allow_null=True)
    ipg['PPP_Perempuan'] = prompt_float('PPP Perempuan: ', allow_null=True)
    ipg['IPM_Laki'] = prompt_float('IPM Laki-laki: ', allow_null=True)
    ipg['IPM_Perempuan'] = prompt_float('IPM Perempuan: ', allow_null=True)
    ipg['IPG'] = prompt_float('IPG: ', allow_null=True)
    ipg['IKG'] = prompt_float('IKG: ', allow_null=True)
    data['ipgData'][year_str] = ipg

    save_json('ipg', data)


def update_idg():
    data = load_json('idg')
    if not data:
        data = {'idgData': {}}

    year = prompt_int('Year to update: ')
    year_str = str(year)

    print(f'\n--- IDG Data for {year} ---')
    idg = {}
    idg['SUMBANGAN'] = prompt_float('Sumbangan %: ', allow_null=True)
    idg['TENAGA'] = prompt_float('Tenaga %: ', allow_null=True)
    idg['PARLEMEN'] = prompt_float('Parlemen %: ', allow_null=True)
    idg['IDG'] = prompt_float('IDG: ', allow_null=True)
    idg['IKG'] = prompt_float('IKG: ', allow_null=True)
    data['idgData'][year_str] = idg

    save_json('idg', data)


def update_sdgs():
    print('SDGs data update is not yet supported by this tool.')
    print('Please edit sdgs_data.json manually.')


UPDATE_HANDLERS = {
    'inflasi': update_inflasi,
    'penduduk': update_penduduk,
    'ipm': update_ipm,
    'kemiskinan': update_kemiskinan,
    'ekonomi': update_ekonomi,
    'pendidikan': update_pendidikan,
    'tenaga_kerja': update_tenaga_kerja,
    'ipg': update_ipg,
    'idg': update_idg,
    'sdgs': update_sdgs,
}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'bump':
        part = sys.argv[2] if len(sys.argv) > 2 else 'patch'
        version = bump_version(part)
        git_commit_push(version)
    elif command == 'list':
        list_status()
    elif command == 'validate':
        ok = validate_all()
        sys.exit(0 if ok else 1)
    elif command in UPDATE_HANDLERS:
        UPDATE_HANDLERS[command]()
        print(f'\nDone! Run "python update_data.py bump" when ready to publish.')
    else:
        print(f'Unknown category: {command}')
        print(f'Available: {", ".join(CATEGORIES)}')
        print(f'Commands: bump, list, validate')
