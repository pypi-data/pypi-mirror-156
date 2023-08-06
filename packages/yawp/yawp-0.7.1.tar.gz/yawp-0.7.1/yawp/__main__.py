#!/usr/bin/python3

#----- imports -----

from .__init__ import __version__ as version, __doc__ as description
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from fnmatch import filter
from warnings import simplefilter
from sys import argv, stdout, stderr
from time import localtime, sleep
from os import remove, rename
from os.path import join as joinpath, split as splitpath, isfile
from .__init__ import longpath, shortpath, splitpath4, listfiles, getfile, lastfile, localfile
from .__init__ import listdirs, getdir, chdir2, newbackfile, oldbackfile
from .__init__ import hold, take, drop, chars, upperin, lowerin, letterin, digitin, specialin, split, replace, change
from .__init__ import shrink, expand, findchar, rfindchar, uppunqshr, titunqshr, nextchar, prevchar, chrs, ords, edit, plural, linterpol
from .__init__ import inform, warning, error, show
from .__init__ import in2in, in2pt, pt2in, in2cm, cm2in, in2mm, mm2in, in2str, str2in, str2inxin, ratio
from .__init__ import retroenum, find, rfind, shell, get, term, tryfunc, dump, ListDict, SetDict
from .__init__ import chapter_level, figure_level

#----- global data -----

class Container: pass
arg = Container() # container for arguments and other scalar global data

#----- constants -----

EMPT, CODE, TEXT, PICT, CONT, FIGU, CAPT, INDX, CHP1, CHP2, HEA1, HEA2 = range(12) # line kinds
KINDS = 'EMPT, CODE, TEXT, PICT, CONT, FIGU, CAPT, INDX, CHP1, CHP2, HEA1, HEA2'.split(', ')
    # EMPT empty line
    # CODE Python code line
    # TEXT text line
    # PICT picture line
    # CONT contents chapter line
    # FIGU figure chapter line
    # CAPT figure caption line
    # INDX index chapter line
    # CHP1 numbered chapter line, level == 1
    # CHP2 numbered chapter line, level > 1
    # HEA1 page header, first line
    # HEA2 page header, second line
JINP, KIND, JPAG, LPIC, LINE = range(5) # positions in buf.input and buf.output
    # JINP line index in input file
    # KIND line kind, see before
    # JPAG page number
    # LPIC number of lines in picture
    # LINE content of line
LABL, TITL, JOUT = range(3) # positions in buf.contents and buf.captions
    # LABL chapter label, as '1.' in buf.contents or '1.a.' in buf.captions
    # TITL chapter title
    # JOUT line index in buf.output
FORMFEED = '\f' # page header, first character of first line
MACRON = '¯' # page header, second line, dashed
QUOTES = "'" + '"' # single and double quotation marks
INDENT = 4 * ' ' # tab indentation
MAX_QUALITY = 5 # max print quality
YAWP_CFG = '~/.yawp/yawp.cfg' # yawp configuration file
PAPERSIZE = { # names for -S
    'HALF LETTER':  '5.5x8.5in',
    'LETTER':       '8.5x11.0in',
    'LEGAL':        '8.5x14.0in',
    'JUNIOR LEGAL': '5.0x8.0in',
    'LEDGER':       '11.0x17.0in',
    'TABLOID':      '11.0x17.0in',
    'A0':  '841x1189mm',
    'A1':  '594x841mm',
    'A2':  '420x594mm',
    'A3':  '297x420mm',
    'A4':  '210x297mm',
    'A5':  '148x210mm',
    'A6':  '105x148mm',
    'A7':  '74x105mm',
    'A8':  '52x74mm',
    'A9':  '37x52mm',
    'A10': '26x37mm',
    'B0':  '1000x1414mm',
    'B1':  '707x1000mm',
    'B1+': '720x1020mm',
    'B2':  '500x707mm',
    'B2+': '520x720mm',
    'B3':  '353x500mm',
    'B4':  '250x353mm',
    'B5':  '176x250mm',
    'B6':  '125x176mm',
    'B7':  '88x125mm',
    'B8':  '62x88mm',
    'B9':  '44x62mm',
    'B10': '31x44mm'}
#
xyxy = {k: [] for k in 'plm llm prm lrm ptm ltm pbm lbm pcw lcw pch lch'.split()}
CONFIG = '''
#----- yawp.cfg ----- yawp configuration file -----

plm 10mm 16mm # portrait left margin
plm 20mm 24mm 
plm 30mm 35mm 
plm 40mm 43mm 
plm 50mm 52mm
plm 60mm 62mm 
plm 70mm 72.5mm 
plm 80mm 83mm 
plm 90mm 92mm 
plm 100mm 101mm 

llm 10mm 20.5mm # landscape left margin
llm 20mm 29.5mm 
llm 30mm 39mm 
llm 40mm 48mm 
llm 50mm 57mm 
llm 60mm 66.5mm 
llm 70mm 75.5mm 
llm 80mm 84.5mm 
llm 90mm 94mm 
llm 100mm 104mm 

prm 10mm 15mm # portrait right margin
prm 20mm 25.5mm 
prm 30mm 34.5mm 
prm 40mm 44.5mm 
prm 50mm 54.5mm 
prm 60mm 64.5mm 
prm 70mm 72mm 
prm 80mm 81mm 
prm 90mm 91.5mm 
prm 100mm 100mm 

lrm 10mm 22mm # landscape left margin
lrm 20mm 30mm 
lrm 30mm 40mm 
lrm 40mm 49.5mm 
lrm 50mm 58mm 
lrm 60mm 68mm 
lrm 70mm 77.5mm 
lrm 80mm 86mm 
lrm 90mm 96mm 
lrm 100mm 104mm 

ptm 10mm 11.5mm # portrait top margin
ptm 20mm 21mm 
ptm 30mm 30.5mm 
ptm 40mm 39.5mm 
ptm 50mm 49mm 
ptm 60mm 59mm 
ptm 70mm 68mm 
ptm 80mm 77.5mm 
ptm 90mm 87mm 
ptm 100mm 96mm 

ltm 10mm 11mm # landscape top margin
ltm 20mm 20.5mm 
ltm 30mm 30mm 
ltm 40mm 39mm 
ltm 50mm 48.5mm 
ltm 60mm 57.5mm 
ltm 70mm 67mm 
ltm 80mm 76mm 
ltm 90mm 85mm 
ltm 100mm 95mm 

pbm 10mm 24mm # portrait bottom margin
pbm 20mm 34mm 
pbm 30mm 43mm 
pbm 40mm 52.5mm 
pbm 50mm 62mm 
pbm 60mm 71mm 
pbm 70mm 81mm 
pbm 80mm 90mm 
pbm 90mm 100mm 
pbm 100mm 109.5mm 

lbm 10mm 24mm # landscape bottom margin
lbm 20mm 32mm 
lbm 30mm 42mm 
lbm 40mm 52mm 
lbm 50mm 60mm 
lbm 60mm 70mm 
lbm 70mm 80mm 
lbm 80mm 88mm 
lbm 90mm 99mm 
lbm 100mm 107mm 

pcw 100mm 94.674mm # portrait character width

lcw 100mm 92.200mm # landscape character width

pch 100mm 94.358mm # portrait character height

lch 100mm 92.647mm # landscape character height
'''

#----- classes -----

class Paragraph:

    def __init__(par):
        par.string = ''
        par.jinp = 0
        par.indent = 0
        
    def assign(par, string, jinp, indent):
        assert not par.string
        par.string = shrink(string)
        par.jinp = jinp
        par.indent = indent
        if indent > arg.half_line:
            error(f"Indent of indented paragraph = {indent} > -w / 2 = {arg.half_line}", jinp, '• ' + string)

    def append(par, string):
        assert par.string
        par.string += ' ' + shrink(string)
        
    def flush(par):
        if not par.string:
            return
        prefix = (par.indent - 2) * ' ' + '• ' if par.indent else ''
        while len(par.string) > arg.chars_per_line - par.indent:
            jchar = rfind(par.string[:arg.chars_per_line-par.indent+1], ' ')
            if jchar <= 0:
                error('Impossible to left-justify', par.jinp, string)
            string, par.string = par.string[:jchar], par.string[jchar+1:]
            if not arg.left_only:
                try:
                    string = expand(string, arg.chars_per_line - par.indent)
                except ValueError:
                    error('Impossible to right-justify', par.jinp, string)
            buf.append(par.jinp, TEXT, 0, 0, prefix + string)
            prefix = par.indent * ' '
        if  par.string:
            buf.append(par.jinp, TEXT, 0, 0, prefix + par.string)
            par.string = ''

par = Paragraph()

class Buffer:

    def __init__(buf):
        buf.input = [] # [[jinp, 0, 0, 0, line]] # input buffer

        buf.output = [] # [[jinp, kind, jpag, lpic, line]] # output buffer
        # jinp: line index in buf.input
        # kind: kind of line: CODE, TEXT, PICT, CONT, INDX, FIGU, CHP1, CHP2, HEA1, HEA2
        # jpag: page number
        # lpic: lines in picture (in first line of pictures only, else 0)
        # line

        buf.contents = [] # [[pref, titl, jout]], if words == line.split() ...
        # pref: words[0], chapter numbering as '1.', '1.1.'...
        # titl: ' '.join(words[1:])
        # jout: position of chapter line in buf.output
        buf.contents_found = False # file contains a contents chapter line?
        buf.contents_jout = -1 # position of contents chapter line in output

        buf.figures_found = False # file contains a figures chapter line?
        buf.figures_jout = -1 # position  of figures chapter line in buf.output
        buf.figures = [] # [[pref, titl, jout]] , if words == line.split() ...
        # words[0] == arg.figures_title
        # pref: words[1], figure numbering as 'a.', '1.b.', '1.1.c.'...
        # titl: ' '.join(words[2:])
        # jout: position of caption line in buf.output

        buf.qsub_jouts = SetDict() # {subject: {jout}}
        # subject: subject between double quotes
        # jout: position of subject in buf.output
        buf.uqsub_jouts = SetDict() # {subject: {jout}}
        # subject: subject not between double quotes
        # jout: position of subject in buf.output
        buf.index_found = False # file contains an index chapter line?
        buf.index_jout = -1 # position of index chapter line in output
        buf.subjects = set()

    def __len__(buf):
        return len(buf.output)

    def append(buf, jinp, kind, jpag, lpic, line):
        buf.output.append([jinp, kind, jpag, lpic, line])

    def char(buf, jout, jchar):
        'return buf.output[jout][LINE][jchar], used by redraw_segments() and redraw_arroheads()'
        if jout < 0 or jchar < 0:
            return ' '
        else:
            try:
                line = buf.output[jout][LINE]
                return line[jchar] if buf.output[jout][KIND] == PICT else ' '
            except IndexError:
                return ' '

    def dump(buf):
        'for debug only'
        print('<' * 72)
        print(f'\n... input ...')
        for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.input):
            print(jout, ':', (jinp, KINDS[kind], jpag, lpic, line))
        print(f'\n... output ...')
        for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.output):
            print(jout, ':', (jinp, KINDS[kind], jpag, lpic, line))
        print('\n... contents ...')
        print(f'... contents_found = {buf.contents_found} ...')
        print(f'... contents_jout = {buf.contents_jout} ...')
        for jout, rec in enumerate(buf.contents):
            print(jout, ':', rec)
        print('\n... figures ...')
        print(f'... figures_found = {buf.figures_found} ...')
        print(f'... figures_jout = {buf.figures_jout} ...')
        for jout, rec in enumerate(buf.figures):
            print(jout, ':', rec)
        print('\n... index ...')
        print(f'... index_found = {buf.index_found} ...')
        print(f'... index_jout = {buf.index_jout} ...')
        for jout, rec in enumerate(buf.qsub_jouts):
            print(jout, ':', rec)
        for jout, rec in enumerate(buf.uqsub_jouts):
            print(jout, ':', rec)
        print('>' * 72)

buf = Buffer()

#----- functions -----

def margin_margin2(letter, margin):    
    x = tryfunc(str2in, (margin,), -1.0)
    if x < 0.0:
        error(f'Wrong -{letter} {margin}')
    if x < str2in('2cm') and arg.verbose:
        if arg.verbose: warning(f'-{letter} {margin} < 2cm, you may get unexpected results')
    margin = x
    if arg.calibration:
        margin2 = margin
    else:
        margin2 = max(0.0, linterpol(xyxy['pl'[arg.landscape] + letter.lower() + 'm'], margin))
        if arg.verbose: inform(f'Correct: -{letter} {in2str(margin2)}')
    return margin, margin2

#----- actions -----

def get_arguments():
    parser = ArgumentParser(prog='yawp', formatter_class=RawDescriptionHelpFormatter, description=description)
    # argument types
    bool = lambda short, long, help: parser.add_argument(short, long, action='store_true', help=help) # boolean argument
    vers = lambda short, long, version: parser.add_argument(short, long, action='version', version=version) # version argument
    stri = lambda short, long, default, help, note='': parser.add_argument( # string argument
        short, long, default=default, help=f"{help} (default: {default!r}{note})".replace('%','%%'))
    posi = lambda name, nargs, help: parser.add_argument(name, nargs=nargs, help=help) # positional argument
    # usage arguments
    bool('-H', '--manual', 'view yawp-generated PDF Yawp Manual and exit')
    vers('-V', '--version', f'yawp {version}')
    bool('-v', '--verbose', 'display information and warning messages on stderr')
    bool('-N', '--no-format', "run in no-format mode (default: run in format mode)")
    bool('-U', '--undo', "run in undo mode (default: run in format mode)")
    bool('-g', '--graphics', "redraw '`'-segments and '^'-arrowheads")
    # formatting arguments
    stri('-w', '--chars-per-line', '0', 'line width in characters per line', ' = automatic')
    bool('-l', '--left-only', "justify text lines at left only (default: at left and right)")
    stri('-c', '--contents-title', 'contents', "title of contents chapter")
    stri('-f', '--figures-title', 'figures', "title of figures chapter")
    stri('-F', '--caption-prefix', 'figure', "first word of figure captions")
    stri('-i', '--index-title', 'index', "title of index chapter")
    # paging arguments:
    bool('-j', '--eject', "insert page headers on full page")
    bool('-J', '--eject-pict-chap', 'insert page headers on full page, on broken picture, and before level-1/contents/figures/index chapters')
    stri('-e', '--even-left', '%n/%N', "headers of even pages, left")
    stri('-E', '--even-right', '%f.%e %Y-%m-%d %H:%M:%S', "headers of even pages, right")
    stri('-o', '--odd-left', '%c', "headers of odd pages, left")
    stri('-O', '--odd-right', '%n/%N', "headers of odd pages, right")
    bool('-a', '--all-pages-E-e', "put in all page headers -E at left and -e at right")
    # PDF arguments
    bool('-X', '--export-view-pdf', "at end export and view PDF file")
    stri('-Y', '--view-pdf-by', 'xdg-open', "viewer for the exported PDF file")
    stri('-P', '--file-pdf', '%P/%f.pdf', "exported PDF file")
    stri('-W', '--char-width', '0', "character width", " = automatic, unit: pt/in/mm/cm")
    stri('-A', '--char-aspect', '3/5', "character aspect ratio = char width / char height", ", '1' = square grid")
    stri('-S', '--paper-size', 'A4', "portrait paper size width x height", " = '210x297mm', unit: pt/in/mm/cm")
    bool('-Z', '--landscape', "turn page by 90 degrees (default: portrait)")
    stri('-L', '--left-margin', '2cm', "left margin", ", unit: pt/in/mm/cm")
    stri('-R', '--right-margin', '-L', "right margin", ", unit: pt/in/mm/cm")
    stri('-T', '--top-margin', '2cm', "top margin", ", unit: pt/in/mm/cm")
    stri('-B', '--bottom-margin', '-T', "bottom margin", ", unit: pt/in/mm/cm")
    bool('-C', '--calibration', "don't correct character size and page margins")
    # positional argument
    posi('file', '?', 'text file to be processed')
    # arguments --> arg.*
    parser.parse_args(argv[1:], arg)

def check_arguments():
    arg.start_time = localtime()[:]
    # -H
    if arg.manual:
        yawp_pdf = localfile('docs/yawp.pdf')
        shell(f'xdg-open {yawp_pdf}')
        exit()
    # file
    if not arg.file:
        error("Mandatory positional argument file not found")
    arg.file = longpath(arg.file)
    arg.PpfeYmdHMS = splitpath4(arg.file) + tuple(('%04d %02d %02d %02d %02d %02d' % arg.start_time[:6]).split())
    # -U -N
    if arg.undo and arg.no_format:
        error("You can't set both -U and -N")
    # -w >= 0
    w = tryfunc(int, (arg.chars_per_line,), -1)
    if w < 0:
        error(f'Wrong -w {arg.chars_per_line}')
    arg.chars_per_line = w
    # -c
    arg.contents_title = uppunqshr(arg.contents_title)
    if not arg.contents_title:
        error("-c '' can't be empty")
    # -i
    arg.index_title = uppunqshr(arg.index_title)
    if not arg.index_title:
        error("-i '' can't be empty")
    # -f
    arg.figures_title = uppunqshr(arg.figures_title)
    if not arg.figures_title:
        error("-f '' can't be empty")
    # -c -i -f
    aaa = [arg.contents_title, arg.index_title, arg.figures_title] 
    if len(set(aaa)) < len(aaa):
        error('-c -i and -f must be all different')
    # -F
    arg.caption_prefix = titunqshr(arg.caption_prefix)
    if not arg.caption_prefix:
        error("-F '' can't be empty")
    if ' ' in arg.caption_prefix:
        error(f"-F {arg.caption_prefix!r} can't contain blanks")    
    # -j -J
    if arg.file.endswith('.py'):
        arg.eject = arg.eject_pict_chap = False
    # -e -E -o -O
    for char, argx in zip('eEoO', [arg.even_left, arg.even_right, arg.odd_left, arg.odd_right]):
        try:
            change(argx, 'PpfeYmdHMSnNc', 'PpfeYmdHMSnNc', '%')
        except ValueError as illegal:
            error(f'Wrong -{char} {argx!r}, illegal {str(illegal)!r}')
    # -X -P
    if arg.export_view_pdf:
        try:
            arg.file_pdf = change(arg.file_pdf, 'PpfeYmdHMS', arg.PpfeYmdHMS, '%')
        except ValueError as illegal:
            error(f'Wrong -P {shortpath(arg.file_pdf)!r}, illegal {str(illegal)!r}')
        arg.file_pdf = longpath(arg.file_pdf)
        if not arg.file_pdf.endswith('.pdf'):
            error(f"Wrong -P {shortpath(arg.file_pdf)!r}, doesn't end with '.pdf'")
    # -W >= 0
    W = tryfunc(str2in, (arg.char_width,), -1.0)
    if W < 0.0:
        error(f'Wrong -W {arg.char_width}')
    arg.char_width = W
    # -A > 0
    A = tryfunc(ratio, (arg.char_aspect,), -1.0)
    if A <= 0.0:
        error(f'Wrong -A {arg.char_aspect}')
    arg.char_aspect = A
    # -S 0 < Sw <= Sh
    Sw, Sh = tryfunc(str2inxin, (PAPERSIZE.get(arg.paper_size.upper(), arg.paper_size),), (-1.0, -1.0))
    if not 0 < Sw <= Sh:
        error(f'Wrong -S {arg.paper_size}')
    arg.paper_width, arg.paper_height = Sw, Sh
    # -Z
    if arg.landscape:
        arg.paper_width, arg.paper_height = arg.paper_height, arg.paper_width
    # -L -R
    if arg.right_margin == '-L':
        arg.right_margin = arg.left_margin
    arg.left_margin, arg.left_margin2 = margin_margin2('L', arg.left_margin)
    arg.right_margin, arg.right_margin2 = margin_margin2('R', arg.right_margin)
    arg.free_width = arg.paper_width - arg.left_margin - arg.right_margin
    if arg.free_width <= 0:
        error('-L and/or -R too big, no horizontal space on paper')
    # -T -B
    if arg.bottom_margin == '-T':
        arg.bottom_margin = arg.top_margin
    arg.top_margin, arg.top_margin2 = margin_margin2('T', arg.top_margin)
    arg.bottom_margin, arg.bottom_margin2 = margin_margin2('B', arg.bottom_margin)
    arg.free_height = arg.paper_height - arg.top_margin - arg.bottom_margin
    if arg.free_height <= 0:
        error('-T and/or -B too big, no vertical space on paper')

def get_configuration():
    if arg.calibration:
        if arg.verbose: inform('Correct: -C is on, no corrections')
    else:
        yawp_cfg = longpath(YAWP_CFG)
        if isfile(yawp_cfg):
            if arg.verbose: inform(f'Correct: Corrections from {YAWP_CFG!r}')
            config = open(yawp_cfg)
        else:
            if arg.verbose: inform(f'Correct: {YAWP_CFG!r} not found, default corrections')
            config = CONFIG.split('\n')
        for jcfg, line in enumerate(config):
            stmt = line.split('#')[0].strip()
            if stmt:
                kyx = stmt.split()
                try:
                    k, y, x = kyx
                except ValueError:
                    error(f'Wrong line in {YAWP_CFG!r}, found {len(kyx)} values instead of 3', jcfg, line)
                if k not in xyxy:
                    error(f'Wrong line in {YAWP_CFG!r}, illegal {k!r}', jcfg, line)
                try:
                    x = str2in(x)
                    assert x > 0.0
                except (ValueError, AssertionError):
                    error(f'Wrong line in {YAWP_CFG!r}, illegal {x!r}', jcfg, line)
                try:
                    y = str2in(y)
                    assert y > 0.0
                except (ValueError, AssertionError):
                    error(f'Wrong line in {YAWP_CFG!r}, illegal {y!r}', jcfg, line)
                xyxy[k].append((x, y))
    
def restore_file():
    backfile = oldbackfile(arg.file)
    if not backfile:
        error(f'Backup file for file {shortpath(arg.file)!r} not found')
    if isfile(arg.file): remove(arg.file)
    rename(backfile, arg.file)
    if arg.verbose: inform(f'Restore: {shortpath(arg.file)!r} <-- {shortpath(backfile)!r}')

def read_file_into(buf_records):
    if not isfile(arg.file):
        error(f'File {shortpath(arg.file)!r} not found')
    header_lines, body_lines, arg.num_pages, max_body_width, max_header_width = 0, 0, 1, 0, 0
    for jinp, line in enumerate(open(arg.file)):
        line = line.replace('\t', INDENT).rstrip()
        if line.startswith(FORMFEED):
            arg.num_pages += 1
            max_header_width = max(max_header_width, len(line) - 1)
            header_lines += 1
            if arg.undo or arg.no_format:
                buf_records.append([jinp, PICT, 1, 0, line])
        elif line.startswith(MACRON):
            max_header_width = max(max_header_width, len(line))
            header_lines += 1
            if arg.undo or arg.no_format:
                buf_records.append([jinp, PICT, 1, 0, line])
        else:
            max_body_width = max(max_body_width, len(line))
            body_lines += 1
            buf_records.append([jinp, PICT, 1, 0, line])
    if arg.verbose: inform(f'Read: yawp <-- {shortpath(arg.file)!r}')
    if arg.verbose: inform(f"    {plural(header_lines, 'header line')}, max {plural(max_header_width, 'char')} per line, {plural(arg.num_pages, 'page')}")
    if arg.verbose: inform(f"    {plural(body_lines, 'body line')}, max {plural(max_body_width, 'char')} per line")
    max_total_width = max(max_header_width, max_body_width)
    if arg.verbose: inform(f"    {plural(header_lines + body_lines, 'total line')}, max {plural(max_total_width, 'char')} per line")
    if not max_body_width:
        error(f'File {shortpath(arg.file)!r}, no printable character found')
    if arg.chars_per_line and not arg.char_width: # -w > 0 and -W == 0
        arg.char_width = arg.free_width / arg.chars_per_line # -W <-- -w
        if arg.verbose: inform(f'Compute: -W {in2str(arg.char_width)}')
        if arg.char_width <= 0:
            error(f'Wrong -W {in2str(arg.char_width)} <= 0')
    elif not arg.chars_per_line and arg.char_width: # -w == 0 and -W > 0
        arg.chars_per_line = int(arg.free_width / arg.char_width) # -w <-- -W
        if arg.verbose: inform(f'Compute: -w {arg.chars_per_line}')
        if arg.chars_per_line <= 0:
            error(f'Wrong -w {in2str(arg.chars_per_line)} <= 0')
    elif not arg.chars_per_line and not arg.char_width: # -w == 0 and -W == 0
        arg.chars_per_line = max_body_width # -w <-- file
        if arg.verbose: inform(f'Compute: -w {arg.chars_per_line}')
        if arg.chars_per_line <= 0:
            error(f'Wrong -w {in2str(arg.chars_per_line)} <= 0')
        arg.char_width = arg.free_width / arg.chars_per_line # -W <-- -w
        if arg.verbose: inform(f'Compute: -W {in2str(arg.char_width)}')
        if arg.char_width <= 0:
            error(f'Wrong -W {in2str(arg.char_width)} <= 0')
    if arg.calibration:
        arg.char_width2 = arg.char_width
    else:
        arg.char_width2 = max(0.0, linterpol(xyxy['pl'[arg.landscape] + 'cw'], arg.char_width))
        if arg.verbose: inform(f'Correct: -W {in2str(arg.char_width2)}')
    arg.chars_per_inch = 1.0 / arg.char_width
    arg.chars_per_margin2 = 1.0 / arg.char_width2
    arg.char_height = arg.char_width / arg.char_aspect
    if arg.verbose: inform(f'Compute: char height {in2str(arg.char_height)}')
    if arg.calibration:
        arg.char_height2 = arg.char_height
    else:
        arg.char_height2 = linterpol(xyxy['pl'[arg.landscape] + 'ch'], arg.char_height)
        if arg.verbose: inform(f'Correct: char height {in2str(arg.char_height2)}')
    arg.lines_per_inch = 1.0 / arg.char_height
    arg.lines_per_margin2 = 1.0 / arg.char_height2
    arg.lines_per_page = int(arg.lines_per_inch * arg.free_height) - 3
    arg.half_line = arg.chars_per_line // 2
 
def justify_input_into_output():
    is_python_file = arg.file.endswith('.py')
    format = not is_python_file 
    for jinp, x, x, x, line in buf.input: # input --> par --> buf.output
        is_switch_line = is_python_file and "\'\'\'" in line
        if is_switch_line:
            format = not format
        if is_switch_line or not format: # Python code
            par.flush()
            buf.append(jinp, CODE, 0, 0, line)
        elif not line: # empty-line
            par.flush()
            buf.append(jinp, EMPT, 0, 0, '')
        else:
            jdot = findchar(line, '[! ]')
            if jdot >= 0 and line[jdot:jdot+2] in ['• ','. ']: # dot-line
                par.flush()
                par.assign(line[jdot+2:], jinp, jdot + 2)
            elif line[0] == ' ': # indented-line
                if par.string:
                    par.append(line)
                else:
                    if len(line) > arg.chars_per_line:
                        error(f'Length of picture line is {len(line)} > -w {arg.chars_per_line}', jinp, line)
                    buf.append(jinp, PICT, 0, 0, line)
            elif par.string: # unindented-line
                par.append(line)
            else:
                par.assign(line, jinp, 0)
    par.flush()
    if is_python_file and format:
        error('Python file, odd number of switch lines')

def delete_redundant_empty_lines():
    '''reduce multiple EMPT lines between TEXT line and TEXT line
    (or between TEXT line and EOF) to one EMPT line only'''
    jout, first, last, kind0 = 0, -1, -1, PICT
    while jout < len(buf.output):
        kind = buf.output[jout][KIND]
        if kind0 == TEXT == kind and 0 < first < last:
            del buf.output[first:last]
            jout -= last - first
        if kind == EMPT:
            if first < 0: first = jout
            last = jout
        else: # kind in [TEXT, PICT, CODE]
            kind0 = kind
            first, last, = -1, -1
        jout += 1
    if kind0 == TEXT and 0 < first < last:
        del buf.output[first:last]

def redraw_segments():
    charstr = '`─│┐│┘│┤──┌┬└┴├┼'
    #          0123456789ABCDEF
    charset = frozenset(charstr)
    for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.output):
        if kind == PICT:
            chars = list(line)
            for jchar, char in enumerate(chars):
                if char in charset:
                    chars[jchar] = charstr[1 * (buf.char(jout, jchar - 1) in charset) +
                                           2 * (buf.char(jout + 1, jchar) in charset) +
                                           4 * (buf.char(jout - 1, jchar) in charset) +
                                           8 * (buf.char(jout, jchar + 1) in charset)]
            buf.output[jout][LINE] = ''.join(chars)
    
def redraw_arrowheads():
    charstr = '^▷△^▽^^^◁^^^^^^^'
    #          0123456789ABCDEF
    charset = frozenset(charstr)
    for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.output):
        if kind == PICT:
            chars = list(line)
            for jchar, char in enumerate(chars):
                if char in charset:
                    chars[jchar] = charstr[1 * (buf.char(jout, jchar - 1) == '─') +
                                           2 * (buf.char(jout + 1, jchar) == '│') +
                                           4 * (buf.char(jout - 1, jchar) == '│') +
                                           8 * (buf.char(jout, jchar + 1) == '─')]
            buf.output[jout][LINE] = ''.join(chars)
            
def renumber_chapters():
    levels = []; max_level = 1; nout = len(buf.output)
    for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.output):
        prev_line = buf.output[jout-1][LINE] if jout > 0 else ''
        next_line = buf.output[jout+1][LINE] if jout + 1 < nout else ''
        if kind == TEXT and line and not prev_line and not next_line:
            words = line.split()
            level = chapter_level(words[0])
            title = uppunqshr(line)
            if level > 0: # numbered chapter line
                if level > max_level:
                    error(f'Numbered chapter level is {level} > {max_level}', jinp, line)
                elif level == len(levels) + 1:
                    levels.append(1)
                else:
                    levels = levels[:level]
                    levels[-1] += 1
                title = uppunqshr(' '.join(words[1:]))
                buf.output[jout][KIND] = CHP1 if level == 1 else CHP2
                buf.output[jout][LINE] = '.'.join(str(level) for level in levels) + '. ' + title
                max_level = len(levels) + 1
            elif title == arg.contents_title: # contents chapter line
                buf.output[jout][KIND] = CONT
                buf.output[jout][LINE] = title
                max_level = 1
            elif title == arg.figures_title: # figures chapter line
                buf.output[jout][KIND] = FIGU
                buf.output[jout][LINE] = title
                max_level = 1
            elif title == arg.index_title: # index chapter line
                buf.output[jout][KIND] = INDX
                buf.output[jout][LINE] = title
                max_level = 1
            else: # no chapter line
                title = ''
 
def add_chapters_to_contents():
    for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.output):
        if kind == CONT:
            if buf.contents_found:
                error('More than one contents line in file', jinp, line)
            buf.contents_found = True
            # contents chapter doesn't list itself
        elif kind == FIGU:
            if buf.figures_found:
                error('More than one figures line in file', jinp, line)
            buf.figures_found = True
            buf.contents.append(['', titunqshr(arg.figures_title), jout])
        elif kind == INDX:
            if buf.index_found:
                error('More than one index line in file', jinp, line)
            buf.index_found = True
            buf.contents.append(['', titunqshr(arg.index_title), jout])
        elif kind in [CHP1, CHP2]:
            prefix, title = (line.split(None, 1) + [''])[:2]
            buf.contents.append([prefix, titunqshr(title), jout])

def add_captions_to_figures():
    if buf.figures_found:
        seek = False
        max_len_caption = 0
        chapter = ''
        letter = prevchar('a')
        for jout, record in enumerate(buf.output):
            jinp, kind, jpag, lpic, line = record
            if kind in [CONT, INDX, FIGU]:
                seek = True
            elif kind in [CHP1, CHP2]:
                seek = False
                chapter = line.split()[0]
                letter = prevchar('a')
            elif not seek and kind == PICT and (
                jout == 0 or buf.output[jout-1][KIND] == EMPT) and (
                jout == len(buf.output) - 1 or buf.output[jout+1][KIND] == EMPT):
                words = titunqshr(line).split()
                if len(words) >= 2:
                    prefix, label, *title = titunqshr(line).split()
                    title = ' '.join(title)
                    if prefix == arg.caption_prefix and figure_level(label.lower()) > 0:
                        if letter == 'z':
                            error('More than 26 figure captions in a single chapter', jinp, line)
                        letter = nextchar(letter)
                        label = f'{chapter}{letter}.'
                        caption = f'{prefix} {label} {title}'
                        max_len_caption = max(max_len_caption, len(caption))
                        blanks = (arg.chars_per_line - len(caption)) // 2 * ' '
##                        if len(blanks) < 6:
##                            error(f'Caption {caption!r} is too long', jinp, line)
                        buf.figures.append((label, title, jout))
                        record[LINE] = blanks + caption
                        record[KIND] = CAPT
                        if jout >= 2 and buf.output[jout - 2][KIND] == PICT:
                            buf.output[jout - 1][KIND] = PICT # paste caption with previous picture
                        
def add_quoted_subjects_to_index():
    if buf.index_found:
        buf.qsub_jouts = SetDict() # {subject: jout}
        quote = False; subject = ''; seek = True
        for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.output):
            if kind in [CONT, FIGU, INDX]:
                seek = False
            elif kind in [CHP1, CHP2]:
                seek = True
            elif seek and kind == TEXT:
                for jchar, char in enumerate(line + ' '):
                    if quote:
                        if (char == '"' and get(line, jchar-1, ' ') not in QUOTES and get(line, jchar+1, ' ') not in QUOTES):
                            subject = shrink(subject)
                            buf.qsub_jouts.add(subject, jout)
                            buf.subjects.add(subject)
                            quote = False
                        else:
                            subject += char
                            if len(subject) > arg.half_line:
                                error(f'Length of subject "{subject}..." > -w / 2 = {arg.half_line}')
                    elif (char == '"' and get(line, jchar-1, ' ') not in QUOTES and get(line, jchar+1, ' ') not in QUOTES):
                        subject = ''
                        quote = True
            else:
                if quote:
                    error('Unpaired \'"\' found while filling the index')
        if quote:
            error('Unpaired \'"\' found while filling the index')

def add_unquoted_subjects_to_index():
    if buf.index_found:
        buf.uqsub_jouts = SetDict() # {subject: jout}
        charset = set(chars('[a-zA-Z0-9]') + ''.join(buf.qsub_jouts.keys()))
        word_jouts = [] # [(word, jout)]
        seek = True
        for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.output):
            if kind in [CONT, FIGU, INDX]:
                seek = False
            elif kind in [CHP1, CHP2]:
                seek = True
            elif seek and kind == TEXT:
                for word in take(line, charset, ' ').split():
                    word_jouts.append((word, jout))
        sub0_subws = ListDict() # {subject.word[0]: subject.word[1:]}
        for subject in buf.qsub_jouts.keys():
            subjectwords = subject.split()
            sub0_subws.append(subjectwords[0], subjectwords[1:])
        for jword_jouts, (sub0, jout) in enumerate(word_jouts):
            if sub0 in sub0_subws:
                for subw in sub0_subws[sub0]:
                    subject = sub0 + ' ' + ' '.join(subw) if subw else sub0
                    if subject == ' '.join(w for w, j in word_jouts[jword_jouts: jword_jouts + len(subw) + 1]):
                        buf.uqsub_jouts.add(subject, jout)
                        buf.subjects.add(subject)

def append_contents_to(output2):
    jinp = output2[-1][JINP]
    output2.append([jinp, TEXT, 0, 0, ''])
    fmt_labl = max((len(labl) for labl, titl, jpag in buf.contents), default=0)
    fmt_titl = max((len(titl) for labl, titl, jpag in buf.contents), default=0)
    for labl, titl, jpag in buf.contents:
        line = f'{INDENT}• {edit(labl, fmt_labl)} {edit(titl, fmt_titl)}'
        if len(line.rstrip()) > arg.chars_per_line:
            error(f'Length of contents chapter line {line!r} is {len(line.rstrip())} > -w = {arg.chars_per_line}') 
        output2.append([jinp, TEXT, 0, 0, line])
    output2.append([jinp, TEXT, 0, 0, ''])

def append_figures_to(output2):
    jinp = output2[-1][JINP]
    output2.append([jinp, TEXT, 0, 0, ''])
    fmt_labl = max((len(labl) for labl, titl, jpag in buf.figures), default=0)
    fmt_titl = max((len(titl) for labl, titl, jpag in buf.figures), default=0)
    for labl, titl, jpag in buf.figures:
        line = f'{INDENT}• {edit(labl, fmt_labl)} {edit(titl, fmt_titl)}'
        if len(line.rstrip()) > arg.chars_per_line:
            error(f'Length of figures chapter line {line!r} is {len(line.rstrip())} > -w = {arg.chars_per_line}') 
        output2.append([jinp, TEXT, 0, 0, line])
    output2.append([jinp, TEXT, 0, 0, ''])

def append_index_to(output2):
    jinp = output2[-1][JINP]
    output2.append([jinp, TEXT, 0, 0, ''])
    room = max((len(subject) for subject in buf.subjects), default=0) + 1
    for subject in sorted(buf.subjects):
        line = f'{INDENT}• {edit(subject, room)}'
        if len(line.rstrip()) > arg.chars_per_line:
            error(f'Length of index chapter line {line!r} is {len(line.rstrip())} > -w = {arg.chars_per_line}') 
        output2.append([jinp, TEXT, 0, 0, line])
    output2.append([jinp, TEXT, 0, 0, ''])

def insert_contents_figures_and_index():
    output2 = []
    copy = True
    for record in buf.output:
        kind = record[KIND]
        if kind == CONT:
            buf.contents_jout = len(output2)
            output2.append(record)
            append_contents_to(output2)
            copy = False
        elif kind == FIGU:
            buf.figures_jout = len(output2)
            output2.append(record)
            append_figures_to(output2)
            copy = False
        elif kind == INDX:
            buf.index_jout = len(output2)
            output2.append(record)
            append_index_to(output2)
            copy = False
        elif kind in [CHP1, CHP2]:
            output2.append(record)
            copy = True
        elif copy:
            output2.append(record)
    buf.output = output2

def count_picture_lines():
    jpic = 0
    for jout, record in retroenum(buf.output):
        if record[KIND] in [PICT, CAPT]:
            jpic += 1
            if jout == 0 or buf.output[jout-1][KIND] not in [PICT, CAPT]:
                buf.output[jout][LPIC] = jpic
        else:
            jpic = 0

def count_pages():
    jpag, jpagline = 1, 0
    for jout, (jinp, kind, zero, lpic, line) in enumerate(buf.output):
        if jpagline >= arg.lines_per_page or arg.eject_pict_chap and (
            lpic < arg.lines_per_page and jpagline + lpic >= arg.lines_per_page or
            arg.eject_pict_chap and kind in [CONT, INDX, FIGU, CHP1] and not (
                jout >= 2 and not buf.output[jout-1][LINE] and buf.output[jout-1][JPAG] > buf.output[jout-2][JPAG])):
            jpag += 1
            jpagline = 0
        else:
            jpagline += 1
        buf.output[jout][JPAG] = jpag
    arg.tot_pages = jpag
    
def add_page_numbers_to_contents():
    if buf.contents_jout > -1:
        fmt_jpag = len(str(buf.output[-1][JPAG])) + 1
        for jcontents, (prefix, titl, jout) in enumerate(buf.contents):
            line = buf.output[buf.contents_jout + 2 + jcontents][LINE] + edit(buf.output[jout][JPAG], fmt_jpag)
            if len(line) > arg.chars_per_line:
                error(f'Length of contents chapter line {line!r} is {len(line)} > -w = {arg.chars_per_line}')
            buf.output[buf.contents_jout + 2 + jcontents][LINE] = line

def add_page_numbers_to_index():
    if buf.index_jout > -1:
        qsub_jpags = SetDict() # {quoted_subject: {jpag}}
        for subject, jouts in buf.qsub_jouts.items():
            for jout in jouts:
                qsub_jpags.add(subject, buf.output[jout][JPAG])
        uqsub_jpags = SetDict() # {unquoted_subject: {jpag}}
        for subject, jouts in buf.uqsub_jouts.items():
            for jout in jouts:
                jpag = buf.output[jout][JPAG]
                if jpag not in qsub_jpags[subject]:
                    uqsub_jpags.add(subject, jpag)
        for jindex, subject in enumerate(sorted(buf.subjects)):
            jpag_strjs = sorted((jpag, f'"{jpag}"' if jpag in qsub_jpags[subject] else str(jpag))
                for jpag in (qsub_jpags[subject] | uqsub_jpags[subject])) # [(jpag, str(jpag))]
            line = buf.output[buf.index_jout + 2 + jindex][LINE] + ', '.join(strj for jpag, strj in jpag_strjs)
            if len(line) > arg.chars_per_line:
                if arg.verbose: warning(f"Index line for subject {subject!r} longer than -w {arg.chars_per_line}, truncated and ended with '...'")
                while True:
                    line = line[:line.rfind(',')]
                    if len(line) + 5 <= arg.chars_per_line:
                        break
                line += ', ...'
            buf.output[buf.index_jout + 2 + jindex][LINE] = line

def add_page_numbers_to_figures():
    if buf.figures_jout > -1:
        fmt_jpag = len(str(buf.output[-1][JPAG])) + 1
        for jfigures, (prefix, title, jout) in enumerate(buf.figures):
            line = buf.output[buf.figures_jout + 2 + jfigures][LINE] + edit(buf.output[jout][JPAG], fmt_jpag)
            if len(line) > arg.chars_per_line:
                error(f'Length of figures chapter line {line!r} is {len(line)} > -w = {arg.chars_per_line}')
            buf.output[buf.figures_jout + 2 + jfigures][LINE] = line
    
def insert_page_headers():
    jout = 0; jpag0 = 1; chapter = ''; npag = buf.output[-1][JPAG]
    header2 = arg.chars_per_line * MACRON
    while jout < len(buf.output):
        jinp, kind, jpag, lpic, line = buf.output[jout]
        if kind in [CONT, INDX, FIGU, CHP1]:
            chapter = titunqshr(line)
        if jpag > jpag0:
            left, right = ((arg.even_right, arg.even_left) if arg.all_pages_E_e else
                           (arg.odd_left, arg.odd_right) if jpag % 2 else
                           (arg.even_left, arg.even_right))
            PpfeYmdHMSnNc = arg.PpfeYmdHMS + (str(jpag), str(npag), chapter)
            left = change(left, 'PpfeYmdHMSnNc', PpfeYmdHMSnNc, '%')
            right = change(right, 'PpfeYmdHMSnNc', PpfeYmdHMSnNc, '%')
            blanks = ' ' * (arg.chars_per_line - len(left) - len(right))
            if not blanks:
                header1 = f'{left} {right}' 
                error(f"Length of header {header1!r} is {len(header1)} > -w {arg.chars_per_line}")
            header1 = f'{FORMFEED}{left}{blanks}{right}'
            buf.output.insert(jout, [0, HEA2, jpag, 0, header2])
            buf.output.insert(jout, [0, HEA1, jpag, 0, header1])
            jout += 2
            jpag0 = jpag
        elif jout >= 3 and not buf.output[jout-1][LINE] and buf.output[jout-3][LINE].startswith(FORMFEED):
            left, right = ((arg.even_right, arg.even_left) if arg.all_pages_E_e else
                           (arg.odd_left, arg.odd_right) if jpag % 2 else
                           (arg.even_left, arg.even_right))
            PpfeYmdHMSnNc = arg.PpfeYmdHMS + (str(jpag), str(npag), chapter)
            left = change(left, 'PpfeYmdHMSnNc', PpfeYmdHMSnNc, '%')
            right = change(right, 'PpfeYmdHMSnNc', PpfeYmdHMSnNc, '%')
            blanks = ' ' * (arg.chars_per_line - len(left) - len(right))
            if not blanks:
                header1 = f'{left} {right}' 
                error(f"Length of header {header1!r} is {len(header1)} > -w {arg.chars_per_line}")
            buf.output[jout-3][LINE] = f'{FORMFEED}{left}{blanks}{right}'
        jout += 1

def backup_file():
    backfile = newbackfile(arg.file, arg.start_time)
    shell(f'mv {arg.file!r} {backfile!r}')
    if arg.verbose: inform(f'Backup: {shortpath(arg.file)!r} --> {shortpath(backfile)!r}')

def rewrite_file():
    header_lines, body_lines, arg.num_pages, max_body_width, max_header_width = 0, 0, 1, 0, 0
    with open(arg.file, 'w') as output:
        for jinp, kind, jpag, lpic, line in buf.output:
            line = line.rstrip()
            print(line, file=output)
            if line.startswith(FORMFEED):
                arg.num_pages += 1
                max_header_width = max(max_header_width, len(line) - 1)
                header_lines += 1
            elif line.startswith(MACRON):
                max_header_width = max(max_header_width, len(line))
                header_lines += 1
            else:
                max_body_width = max(max_body_width, len(line))
                body_lines += 1
    if arg.verbose: inform(f"Rewrite: yawp --> {shortpath(arg.file)!r}")
    if arg.verbose: inform(f"    {plural(header_lines, 'header line')}, max {plural(max_header_width, 'char')} per line, {plural(arg.num_pages, 'page')}")
    if arg.verbose: inform(f"    {plural(body_lines, 'body line')}, max {plural(max_body_width, 'char')} per line")
    max_total_width = max(max_header_width, max_body_width)
    if arg.verbose: inform(f"    {plural(header_lines + body_lines, 'total line')}, max {plural(max_total_width, 'char')} per line")

#--------------------------------------------------------------------------

def undo_mode():
    restore_file()
    read_file_into(buf.output)

def no_format_mode():
    read_file_into(buf.output)
    if arg.graphics: # -g ?
        redraw_segments()
        redraw_arrowheads()
    backup_file()
    rewrite_file()

def format_mode():
    read_file_into(buf.input)
    justify_input_into_output()
    delete_redundant_empty_lines()
    if arg.graphics: # -g ?
        redraw_segments()
        redraw_arrowheads()
    renumber_chapters()
    add_chapters_to_contents()
    add_captions_to_figures()
    add_quoted_subjects_to_index()
    add_unquoted_subjects_to_index()
    insert_contents_figures_and_index()
    if arg.eject or arg.eject_pict_chap: # -j or -J ?
        count_picture_lines()
        count_pages()
        add_page_numbers_to_contents()
        add_page_numbers_to_figures()
        add_page_numbers_to_index()
        insert_page_headers()
    backup_file()
    rewrite_file()

def export_output_into_file_pdf():
    shell(f'lp -d PDF '
          f'-o print-quality={MAX_QUALITY} '
          f'-o media=Custom.{in2pt(arg.paper_width)}x{in2pt(arg.paper_height)} '
          f'-o cpi={arg.chars_per_margin2} '
          f'-o lpi={arg.lines_per_margin2} '
          f'-o page-top={in2pt(arg.top_margin2)} '
          f'-o page-left={in2pt(arg.left_margin2)} '
          f'-o page-right={0 if arg.num_pages > 1 else in2pt(arg.right_margin2)} '
          f'-o page-bottom={0 if arg.num_pages > 1 else in2pt(arg.bottom_margin2)} '
          f'{arg.file!r}')
    while True: # wait lp completion
        sleep(0.1)
        lines = shell(f'lpq -P PDF')
        if not any(line.startswith('active') for line in lines):
            break
    file_pdf = lastfile('~/PDF/*.pdf')
    if not file_pdf:
        error('Exported PDF file not found')
    if isfile(arg.file_pdf): remove(arg.file_pdf)
    rename(file_pdf, arg.file_pdf)
    if arg.verbose: inform(f'Export: {shortpath(arg.file)!r} --> {shortpath(arg.file_pdf)!r}')

def view_file_pdf():
    shell(f'{arg.view_pdf_by} {arg.file_pdf}')

#--------------------------------------------------------------------------

def main():
    try:
        simplefilter('ignore')
        get_arguments()
        get_configuration()
        check_arguments()
        if arg.undo: # -U ?
            undo_mode()
        elif arg.no_format: # -N ?
            no_format_mode()
        else: # not -U and not -N
            format_mode()
        if arg.export_view_pdf: # -X ?
            export_output_into_file_pdf()
            view_file_pdf()
    except KeyboardInterrupt:
        print()

if __name__ == '__main__':
    main()

#----- end -----
