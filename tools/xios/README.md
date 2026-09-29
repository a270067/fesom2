# XIOS definition files for FESOM2

XIOS writes only fields that are declared in `field_def_fesom.xml` and
silently drops every other field the model sends. The hand-written templates
declared 66 fields; `gen_xios_xml.py` declares every output stream of
`src/io_meandata.F90`.

## Generate the definitions

```bash
python3 tools/xios/gen_xios_xml.py                # -> docs/xios_xml/{field,grid,axis}_def_fesom.xml
python3 tools/xios/gen_xios_xml.py -o <rundir>    # directly into a run directory
python3 tools/xios/gen_xios_xml.py --recom        # also REcoM fields
python3 tools/xios/gen_xios_xml.py --tracer-ids 101 102   # passive tracers tra_0101, tra_0102
```

* 371 physical fields on 11 grids: 2-D nodes/elements, 3-D layers and
  level interfaces on nodes/elements, dMOC density classes, IDEMIX2 spectral
  bins, global scalars (CMOR).
* `detect_missing_value="true"` for all fields: points masked by the model
  (below the sea floor, under ice shelves, ice fields without ice) do not
  enter the time means.
* `standard_name` attributes of an existing `field_def` are kept.
* Re-run the generator after adding or renaming a stream in `io_meandata.F90`.
* `domain_def`, `context`, `iodef` and `file_def` are not touched. The new
  `grid_def` needs the axes `std_dens` and `nfbin` of the new `axis_def`.

## Choose what is written

A field is computed only if its switch is on (`io_list` id, `&diag_list`
flag or the corresponding XML variable in `context_fesom.xml`) and written
only if `file_def_fesom.xml` asks for it. At start-up `fesom.x` writes
`fesom_xios_streams.txt` into the run directory: every stream registered in
this configuration, its size and whether `field_def` declares it (T/F). The
log reports how many are declared. From that list

```bash
python3 tools/xios/gen_file_def.py --streams fesom_xios_streams.txt --freq 1mo > file_def_fesom.xml
python3 tools/xios/gen_file_def.py --group 1d:sst,ssh,a_ice --group 1mo:temp,salt,u,v,w > file_def_fesom.xml
```

## Notes

* XIOS axis names: `nz` = layer mid-depths (nl-1), `nz1` = level interfaces
  (nl), the opposite of the native netCDF output.
* `nfbin` (IDEMIX2 spectral bins) is sized at run time from
  `idemix2_nfbin` in `&param_idemix2` of `namelist.cvmix` (default 52).
* Streams on the nextGEMS "upper" levels are not available with XIOS.
