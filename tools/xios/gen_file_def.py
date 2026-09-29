#!/usr/bin/env python3
"""Write a file_def_fesom.xml (one netCDF file per variable).

Examples
  # every stream the model registered in this configuration (list written by
  # fesom.x at start-up in XIOS mode), monthly means:
  python3 gen_file_def.py --streams fesom_xios_streams.txt --freq 1mo > file_def_fesom.xml
  # selected variables, several frequencies:
  python3 gen_file_def.py --group 1d:sst,ssh,a_ice --group 1mo:temp,salt,u,v,w > file_def_fesom.xml

Variables that are not declared in field_def are skipped when --streams is
used (last column F in fesom_xios_streams.txt).
"""
import argparse, sys
from xml.sax.saxutils import quoteattr

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--streams', help='fesom_xios_streams.txt written by fesom.x')
ap.add_argument('--freq', default='1mo', help='output_freq for --streams (e.g. 1d, 1mo, 1y, 6h)')
ap.add_argument('--group', action='append', default=[], help='FREQ:var1,var2,... (repeatable)')
ap.add_argument('--split', default='1y', help='split_freq of all files')
ap.add_argument('--suffix', default='fesom', help='file name = <var>.<suffix>')
ap.add_argument('--exclude', default='', help='comma-separated variables to leave out')
a = ap.parse_args()

groups = []
excl = set(x for x in a.exclude.split(',') if x)
if a.streams:
    names = []
    for line in open(a.streams):
        if line.startswith('#') or not line.strip(): continue
        f = line.split()
        if f[-1].upper() == 'T' and f[0] not in excl and f[0] not in names: names.append(f[0])
    groups.append((a.freq, names))
for g in a.group:
    freq, vs = g.split(':', 1)
    groups.append((freq, [v for v in vs.split(',') if v and v not in excl]))
if not groups: ap.error('give --streams or --group')

o = ['<?xml version="1.0"?>',
     '<file_definition type="one_file" format="netcdf4" par_access="collective"',
     '                 time_counter_name="time" time_counter="exclusive">']
for i, (freq, names) in enumerate(groups):
    o.append('  <file_group id="fesom_%s_%d" output_freq="%s" split_freq="%s" enabled="true">' % (freq, i, freq, a.split))
    for n in names:
        o.append('    <file id=%s name=%s><field field_ref=%s/></file>' % (
            quoteattr('f_%s_%d' % (n, i)), quoteattr('%s.%s' % (n, a.suffix)), quoteattr(n)))
    o.append('  </file_group>')
o.append('</file_definition>')
sys.stdout.write('\n'.join(o) + '\n')
