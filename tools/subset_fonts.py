"""Cut the interface fonts into the small WOFF2 files in web/ (font-*.woff2).

Development only: needs fonttools and brotli, which production does not install
(python -m pip install fonttools brotli, ideally in a virtual environment).

Source fonts (SIL OFL 1.1, licences in docs/licenses/) come from the google/fonts
repository, folder ofl/: bevietnampro/BeVietnamPro-Regular.ttf, -SemiBold.ttf,
-Bold.ttf; baloo2/Baloo2[wght].ttf; notoseriftc/NotoSerifTC[wght].ttf. Put them in
one folder and pass it with --source.

    python tools/subset_fonts.py --source FOLDER   # rebuild every web/font-*.woff2
    python tools/subset_fonts.py --check           # list Han characters the font lacks

Latin and Vietnamese text keep the full Latin + Vietnamese range. The Han font
keeps only the characters found in web/*.js, web/*.css and web/index.html (pieces,
chapter marks), so adding a new character to the interface needs a rebuild; until
then the browser draws it with a system font. Run tools/stamp_static_versions.py
afterwards. Exit code: 0 = done or nothing missing, 1 = characters missing,
2 = fonttools/brotli or a source file is missing.
"""
from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
HAN = re.compile(r'[㐀-鿿豈-﫿]')
LATIN_VI = ('U+0020-007E,U+00A0-00FF,U+0100-017F,U+0131,U+0152-0153,U+01A0-01A1,U+01AF-01B0,U+02BB-02BC,'
            'U+02C6,U+02DA,U+02DC,U+0300-0301,U+0303-0304,U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,'
            'U+2010-2027,U+2030-203A,U+20AB,U+20AC,U+2122,U+2190-2199,U+2212,U+221E,U+2713')
# (source file, output in web/, characters, variable-font weight: one value or a (min, max) range)
FONTS = [
    ('BeVietnamPro-Regular.ttf', 'font-be-vietnam-pro-400.woff2', 'latin', None),
    ('BeVietnamPro-SemiBold.ttf', 'font-be-vietnam-pro-600.woff2', 'latin', None),
    ('BeVietnamPro-Bold.ttf', 'font-be-vietnam-pro-700.woff2', 'latin', None),
    ('Baloo2[wght].ttf', 'font-baloo-2.woff2', 'latin', (600, 800)),
    ('NotoSerifTC[wght].ttf', 'font-noto-serif-tc-900.woff2', 'han', 900),
]
HAN_OUTPUT = 'font-noto-serif-tc-900.woff2'


def used_han(web=WEB):
    """Every Han character the interface shows, from scripts, styles and index.html."""
    found = set()
    for path in [*web.glob('*.js'), *web.glob('*.css'), web / 'index.html']:
        found |= set(HAN.findall(path.read_text(encoding='utf-8')))
    return found


def load_fonttools():
    try:
        import brotli  # noqa: F401  (WOFF2 needs it)
        from fontTools import subset
        from fontTools.ttLib import TTFont
        from fontTools.varLib import instancer
    except ImportError:
        print('Needs fonttools and brotli: python -m pip install fonttools brotli')
        sys.exit(2)
    return subset, TTFont, instancer


def build(source):
    subset, TTFont, instancer = load_fonttools()
    han = ','.join('U+%04X' % ord(c) for c in sorted(used_han()))
    for name, output, chars, weight in FONTS:
        path = Path(source) / name
        if not path.is_file():
            print('Missing source font: ' + str(path))
            return 2
        font = TTFont(path)
        options = subset.Options()
        options.flavor = 'woff2'
        options.layout_features = ['kern', 'liga', 'mark', 'mkmk', 'ccmp', 'locl']
        options.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]  # keep copyright, licence and URL records
        options.notdef_outline = True
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=subset.parse_unicodes(LATIN_VI if chars == 'latin' else han))
        subsetter.subset(font)
        if weight is not None:
            font = instancer.instantiateVariableFont(font, {'wght': weight})
        font.flavor = 'woff2'
        font.save(WEB / output)
        print(f'{output}: {(WEB / output).stat().st_size} bytes')
    print('Next: python tools/stamp_static_versions.py')
    return 0


def check():
    _, TTFont, _ = load_fonttools()
    cmap = TTFont(WEB / HAN_OUTPUT).getBestCmap()
    missing = sorted(c for c in used_han() if ord(c) not in cmap)
    if missing:
        print('The Han font lacks: ' + ' '.join(missing))
        print('Rebuild: python tools/subset_fonts.py --source FOLDER')
        return 1
    print('PASS: the Han font covers every character the interface uses.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--source', help='Folder with the source .ttf files')
    group.add_argument('--check', action='store_true', help='List Han characters missing from the font')
    args = parser.parse_args()
    return check() if args.check else build(args.source)


if __name__ == '__main__':
    sys.exit(main())
