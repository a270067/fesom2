! ============================================================================
! ============ Namelist file for FESOM2 output configuration =================
! ============================================================================
! Even with XIOS handling actual output (file_def_fesom.xml), FESOM2.8.0
! still reads this file at startup for &diag_list (diagnostic flags -
! xios_getvar() in io_xios_init can override individual ones from
! context_fesom.xml, but the block must exist here as the base) and
! &nml_general/&nml_list. This file was missing entirely in the first two
! submissions -- "ERROR: Could not open namelist file namelist.io" was the
! second crash's root cause.
! ============================================================================

&diag_list
ldiag_solver      = .false.
lcurt_stress_surf = .false.
ldiag_curl_vel3   = .false.
ldiag_Ri          = .false.
ldiag_turbflux    = .false.
ldiag_salt3D      = .false.
ldiag_dMOC        = .false.
ldiag_diapmix     = .false.
diap_call_freq    = 1
diap_call_freq_unit = 'd'
ldiag_DVD         = .false.
ldiag_forc        = .false.
ldiag_extflds     = .false.
ldiag_destine     = .false.
ldiag_trflx       = .false.
ldiag_uvw_sqr     = .false.
ldiag_trgrd_xyz   = .false.
ldiag_cmor        = .false.
/

&nml_general
io_listsize       = 100      ! matches old palk value; >= number of streams in &nml_list below (21)
vec_autorotate    = .false.  ! palk value
compression_level = 0        ! 2.8.0-only, no old-palk precedent -> stock/jack_6 default
/

! Same 23-field list as palk's old namelist.io &nml_list (2026-09-18: unod30/
! vnod30 added back -- see file_def_fesom.xml for why they turned out not
! to need custom XIOS axis work after all).
&nml_list
io_list =  'sst       ',1, 'd', 4,
           'sss       ',1, 'd', 4,
           'ssh       ',1, 'd', 4,
           'uice      ',1, 'd', 4,
           'vice      ',1, 'd', 4,
           'a_ice     ',1, 'd', 4,
           'm_ice     ',1, 'd', 4,
           'm_snow    ',1, 'm', 4,
           'MLD1      ',1, 'm', 4,
           'MLD2      ',1, 'm', 4,
           'MLD3      ',1, 'm', 4,
           'tx_sur    ',1, 'm', 4,
           'ty_sur    ',1, 'm', 4,
           'temp      ',1, 'm', 4,
           'salt      ',1, 'm', 4,
           'N2        ',1, 'm', 4,
           'u         ',1, 'm', 4,
           'v         ',1, 'm', 4,
           'unod      ',1, 'm', 4,
           'vnod      ',1, 'm', 4,
           'unod30    ',1, 'm', 4,
           'vnod30    ',1, 'm', 4,
           'w         ',1, 'm', 4,
/
