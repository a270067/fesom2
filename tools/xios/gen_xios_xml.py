#!/usr/bin/env python3
"""Generate the XIOS definition files of FESOM2 from src/io_meandata.F90.

Every output stream of io_meandata.F90 (def_stream / def_stream0D) is declared
as an XIOS field on the grid that matches its shape, so that file_def can
request any of them. XIOS silently drops fields that are not declared, which
is why the hand-written templates (66 fields) only allowed a small subset.

Usage (from the repository root):
    python3 tools/xios/gen_xios_xml.py                 # physical fields only
    python3 tools/xios/gen_xios_xml.py --recom         # include REcoM (__recom)
    python3 tools/xios/gen_xios_xml.py --tracer-ids 101 102   # passive tracers tra_0101 ...
    python3 tools/xios/gen_xios_xml.py -o work/xios     # output directory

Writes field_def_fesom.xml, grid_def_fesom.xml and axis_def_fesom.xml
(domain_def_fesom.xml, context_fesom.xml, iodef.xml and file_def_fesom.xml are
not touched). Streams on the 'upper' levels (nlev_upper, nextGEMS set) are not
declared: in XIOS mode nlev_upper is 1 and they are not registered.
"""
import argparse, os, re, sys
from xml.sax.saxutils import quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

# grid of a stream, from the dimension expression of def_stream (lower case, no blanks)
GRID = {
    'nod2d':                   ('grid_2d_nod',       '2D fields on nodes'),
    'elem2d':                  ('grid_2d_elem',      '2D fields on elements'),
    '(/nl-1,nod2d/)':          ('grid_3d_nod',       '3D fields on nodes, layers (XIOS axis nz = nl-1)'),
    '(/nl,nod2d/)':            ('grid_3d_nod_nz1',   '3D fields on nodes, level interfaces (XIOS axis nz1 = nl)'),
    '(/nl-1,elem2d/)':         ('grid_3d_elem',      '3D fields on elements, layers'),
    '(/nl,elem2d/)':           ('grid_3d_elem_nz1',  '3D fields on elements, level interfaces'),
    '(/std_dens_n,nod2d/)':    ('grid_dens_nod',     'density-class fields on nodes (dMOC)'),
    '(/std_dens_n,elem2d/)':   ('grid_dens_elem',    'density-class fields on elements (dMOC)'),
    '(/idemix2_nfbin,nod2d/)': ('grid_nfbin_nod',    'IDEMIX2 spectral-bin fields on nodes'),
    '(/idemix2_nfbin,elem2d/)':('grid_nfbin_elem',   'IDEMIX2 spectral-bin fields on elements'),
    '0d':                      ('grid_scalar',       'global scalars (CMOR)'),
}
SKIP_DIMS = ('nlev_upper',)

def parse(path, want_recom):
    lines = open(path, errors='ignore').read().split('\n')
    stack, recs, buf, bline, case = [], [], '', 0, None
    for i, raw in enumerate(lines, 1):
        st = raw.strip()
        if st.startswith(('#if', '#ifdef', '#ifndef')): stack.append(st); continue
        if st.startswith('#elif'): stack[-1] = st; continue
        if st.startswith('#else'): stack[-1] = '!(' + stack[-1] + ')'; continue
        if st.startswith('#endif'): stack.pop(); continue
        m = re.match(r"\s*CASE\s*\(\s*'([^']*)'", raw, re.I)
        if m: case = m.group(1).strip()
        code = raw.split('!')[0] if "'" not in raw else raw  # keep strings intact
        if buf:
            buf += ' ' + code.strip().lstrip('&')
        elif re.search(r'call\s+def_stream(0D)?\s*\(', code, re.I) and not raw.lstrip().startswith('!'):
            buf, bline = code.strip(), i
        if buf:
            if buf.rstrip().endswith('&'):
                buf = buf.rstrip()[:-1]; continue
            recs.append((bline, ' && '.join(stack), case, buf)); buf = ''
    out = []
    for line, ctx, case, text in recs:
        if ('__recom' in ctx) and not want_recom: continue
        m = re.search(r'call\s+def_stream(0D)?\s*\((.*)\)\s*$', text, re.I)
        if not m: continue
        zero, args = bool(m.group(1)), m.group(2)
        parts, depth, cur, q = [], 0, '', None
        for ch in args:
            if q:
                cur += ch
                if ch == q: q = None
                continue
            if ch in "'\"": q = ch; cur += ch; continue
            if ch == '(': depth += 1
            if ch == ')': depth -= 1
            if ch == ',' and depth == 0: parts.append(cur.strip()); cur = ''; continue
            cur += ch
        parts.append(cur.strip())
        if zero: dims, name, lname, unit = '0d', parts[0], parts[1], parts[2]
        else:    dims, name, lname, unit = parts[0], parts[2], parts[3], parts[4]
        out.append(dict(line=line, ctx=ctx, case=case, dims=dims.replace(' ', '').lower(),
                        name=name, lname=lname, unit=unit))
    return out

def lit(s):
    s = s.strip()
    m = re.fullmatch(r"'([^']*)'|\"([^\"]*)\"", s)
    return (m.group(1) if m.group(1) is not None else m.group(2)).strip() if m else None

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', default=os.path.join(ROOT, 'src', 'io_meandata.F90'))
    ap.add_argument('-o', '--outdir', default=os.path.join(ROOT, 'docs', 'xios_xml'))
    ap.add_argument('--recom', action='store_true', help='include REcoM fields')
    ap.add_argument('--tracer-ids', type=int, nargs='*', default=[], help='IDs of passive tracers (tra_NNNN)')
    ap.add_argument('--keep-attrs', default=os.path.join(ROOT, 'docs', 'xios_xml', 'field_def_fesom.xml'),
                    help='existing field_def whose extra attributes (standard_name, ...) are kept for matching ids')
    a = ap.parse_args()
    recs = parse(a.src, a.recom)
    # extra attributes of an existing field_def (read before it may be overwritten)
    keep = {}
    if a.keep_attrs and os.path.exists(a.keep_attrs):
        for m in re.finditer(r'<field\s+id="([^"]+)"([^>]*?)/?>', open(a.keep_attrs).read()):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(2)))
            extra = {k: v for k, v in attrs.items() if k in ('standard_name', 'long_name', 'unit')}
            if extra: keep[m.group(1)] = extra
    fields, skipped = {}, []
    tf = [('utemp', 'u*temp', 'm/s*degC'), ('vtemp', 'v*temp', 'm/s*degC'),
          ('usalt', 'u*salt', 'm/s*psu'), ('vsalt', 'v*salt', 'm/s*psu')]
    for r in recs:
        if any(k in r['dims'] for k in SKIP_DIMS): skipped.append(r); continue
        grid = GRID.get(r['dims'])
        if grid is None: skipped.append(r); continue
        name = lit(r['name'])
        if name is None:
            if 'tf_names' in r['name']:           # tracer-flux diagnostics
                for n, ln, u in tf: fields.setdefault(n, (grid[0], ln, u, r))
            elif "'tra_'//" in r['name']:          # passive tracers
                for tid in a.tracer_ids:
                    fields.setdefault('tra_%04d' % tid, (grid[0], 'passive tracer ID=%04d' % tid, 'n/a', r))
            else:
                skipped.append(r)
            continue
        ln, un = lit(r['lname']) or name, lit(r['unit']) or ''
        fields.setdefault(name, (grid[0], ln.replace('\\n', ' '), un, r))
    os.makedirs(a.outdir, exist_ok=True)
    # ---------------- field_def
    bygrid = {}
    for n, (g, ln, u, r) in fields.items(): bygrid.setdefault(g, []).append((n, ln, u, r))
    L = ['<?xml version="1.0"?>',
         '<!-- Generated by tools/xios/gen_xios_xml.py from src/io_meandata.F90: every',
         '     %s output stream of FESOM2 (%d fields). Do not edit by hand;' % ('' if a.recom else 'physical (non-REcoM)', len(fields)),
         '     re-run the generator after changing io_meandata.F90. A field is only',
         '     computed if its switch (io_list id or &diag_list flag, see comments)',
         '     is active; it is only written if file_def_fesom.xml requests it. -->',
         '<!-- detect_missing_value: masked points (below the sea floor, under ice',
         '     shelves, ice fields where there is no ice) are sent as the fill value',
         '     and excluded from the time means. -->',
         '<field_definition level="1" prec="4" enabled="true" operation="average"',
         '                  default_value="9.969209968386869e+36" detect_missing_value="true">']
    for g, desc in [v for v in GRID.values()]:
        if g not in bygrid: continue
        L.append('')
        L.append('  <!-- %s -->' % desc)
        prec = ' prec="8"' if g == 'grid_scalar' else ''
        L.append('  <field_group id="fesom_%s" grid_ref="%s"%s>' % (g.replace('grid_', ''), g, prec))
        for n, ln, u, r in sorted(bygrid[g], key=lambda x: x[0].lower()):
            src = 'io_list: %s' % r['case'] if r['case'] else 'diagnostic'
            if r['ctx']: src += '; ' + r['ctx'].replace('#if ', '').replace('defined', '').replace('  ', ' ')
            k = keep.get(n, {})
            ln2, u2 = k.get('long_name', ln), k.get('unit', u)
            sn = (' standard_name=%s' % quoteattr(k['standard_name'])) if 'standard_name' in k else ''
            L.append('    <field id=%s long_name=%s%s unit=%s/> <!-- %s -->' % (quoteattr(n), quoteattr(ln2), sn, quoteattr(u2), src.replace('--', '-')))
        L.append('  </field_group>')
    L.append('</field_definition>')
    open(os.path.join(a.outdir, 'field_def_fesom.xml'), 'w').write('\n'.join(L) + '\n')
    # ---------------- grid_def
    G = ['<?xml version="1.0"?>', '<!-- Generated by tools/xios/gen_xios_xml.py. Axis-first composition matches the',
         '     Fortran send buffers (nlev, npoints). -->', '<grid_definition>']
    def grid(gid, desc, axis, dom):
        G.append('  <grid id="%s" description="%s">' % (gid, desc))
        if axis: G.append('    <axis   axis_ref="%s"/>' % axis)
        G.append('    <domain domain_ref="%s"/>' % dom)
        G.append('  </grid>')
    grid('grid_2d_nod', '2D grid on FESOM nodes', None, 'nodes')
    grid('grid_2d_elem', '2D grid on FESOM elements', None, 'elements')
    grid('grid_3d_nod', '3D grid on FESOM nodes, layers', 'nz', 'nodes')
    grid('grid_3d_elem', '3D grid on FESOM elements, layers', 'nz', 'elements')
    grid('grid_3d_nod_nz1', '3D grid on FESOM nodes, level interfaces', 'nz1', 'nodes')
    grid('grid_3d_elem_nz1', '3D grid on FESOM elements, level interfaces', 'nz1', 'elements')
    grid('grid_dens_nod', 'density classes x nodes (dMOC)', 'std_dens', 'nodes')
    grid('grid_dens_elem', 'density classes x elements (dMOC)', 'std_dens', 'elements')
    grid('grid_nfbin_nod', 'IDEMIX2 spectral bins x nodes', 'nfbin', 'nodes')
    grid('grid_nfbin_elem', 'IDEMIX2 spectral bins x elements', 'nfbin', 'elements')
    G.append('  <grid id="grid_scalar" description="global scalar">')
    G.append('    <scalar/>')
    G.append('  </grid>')
    G.append('</grid_definition>')
    open(os.path.join(a.outdir, 'grid_def_fesom.xml'), 'w').write('\n'.join(G) + '\n')
    # ---------------- axis_def
    X = ['<?xml version="1.0"?>',
         '<!-- Generated by tools/xios/gen_xios_xml.py. n_glo and value are set at run time',
         '     by io_xios_init. NOTE: in XIOS nz = layer mid-depths (nl-1 values) and',
         '     nz1 = level interfaces (nl values), the opposite of the native netCDF',
         '     output where nz has nl and nz1 has nl-1 values. -->',
         '<axis_definition>',
         '  <axis_group id="fesom_axes" unit="m" positive="down" axis_type="Z">',
         '    <axis id="nz"  long_name="depth below sea level at layer mid-points" standard_name="depth" />',
         '    <axis id="nz1" long_name="depth below sea level at layer interfaces" standard_name="depth" />',
         '  </axis_group>',
         '  <axis id="std_dens" unit="kg/m^3" long_name="potential density (sigma2) for dMOC" standard_name="sea_water_potential_density" />',
         '  <axis id="nfbin" unit="1" long_name="IDEMIX2 spectral bin" />',
         '</axis_definition>']
    open(os.path.join(a.outdir, 'axis_def_fesom.xml'), 'w').write('\n'.join(X) + '\n')
    print('declared %d fields on %d grids -> %s' % (len(fields), len(bygrid), a.outdir))
    for g in sorted(bygrid): print('  %-18s %4d' % (g, len(bygrid[g])))
    if skipped:
        print('not declared (%d):' % len(skipped))
        for r in skipped: print('   line %5d  %-28s %s' % (r['line'], r['name'][:28], r['dims']))

if __name__ == '__main__':
    main()
