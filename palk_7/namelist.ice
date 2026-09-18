! ============================================================================
! ============== Namelist file for FESOM2 sea ice model =====================
! ============================================================================
! palk_7 on FESOM2.8.0. Structure = 2.8.0 stock template
! (/home/a/a270067/fesom2-2.8.0/config/namelist.ice); values below carried
! over from the old palk_7 config where a matching parameter name existed
! there, otherwise left at the 2.8.0 stock default (noted per line).
! All &ice_dyn values below happen to be identical between old palk_7 and
! the 2.8.0 stock default - no real differences in this block.
! ============================================================================

&ice_dyn
whichEVP       = 0              ! old palk_7 value (same as stock default)
Pstar          = 30000.0        ! old palk_7 value (same as stock default)
ellipse        = 2.0            ! old palk_7 value (same as stock default)
c_pressure     = 20.0           ! old palk_7 value (same as stock default)
delta_min      = 1.0e-11        ! old palk_7 value (same as stock default)
evp_rheol_steps = 120           ! old palk_7 value (same as stock default)
alpha_evp      = 250            ! old palk_7 value (same as stock default)
beta_evp       = 250            ! old palk_7 value (same as stock default)
c_aevp         = 0.15           ! old palk_7 value (same as stock default)
Cd_oce_ice     = 0.0055         ! old palk_7 value (same as stock default)
ice_gamma_fct  = 0.5            ! old palk_7 value (same as stock default)
ice_diff       = 0.0            ! old palk_7 value (same as stock default)
theta_io       = 0.0            ! old palk_7 value (same as stock default)
ice_ave_steps  = 1              ! old palk_7 value (same as stock default)
/

&ice_therm
Sice           = 4.0            ! old palk_7 value (same as stock default)
iclasses       = 7              ! 2.8.0-only, no old-palk precedent -> stock default
new_iclasses   = .false.        ! 2.8.0-only, no old-palk precedent -> stock default
h_cutoff       = 3.0            ! 2.8.0-only, no old-palk precedent -> stock default
h0             = 0.5            ! old palk_7 value (same as stock default)
h0_s           = 0.5            ! 2.8.0-only, no old-palk precedent -> stock default
hmin           = 0.01           ! 2.8.0-only, no old-palk precedent -> stock default
armin          = 0.01           ! 2.8.0-only, no old-palk precedent -> stock default
emiss_ice      = 0.97           ! old palk_7 value (same as stock default)
emiss_wat      = 0.97           ! old palk_7 value (same as stock default)
albsn             = 0.81           ! old palk_7 value (same as stock default)
albsnm            = 0.77           ! old palk_7 value (same as stock default)
albi              = 0.7            ! old palk_7 value (same as stock default)
albim             = 0.68           ! old palk_7 value (same as stock default)
albw              = 0.1            ! old palk_7 value (same as stock default)
open_water_albedo = 0           ! 2.8.0-only, no old-palk precedent -> stock default
con            = 2.1656         ! old palk_7 value (same as stock default)
consn          = 0.31           ! old palk_7 value (same as stock default)
snowdist       = .true.         ! 2.8.0-only, no old-palk precedent -> stock default
h_snowscale    = 0.0            ! 2.8.0-only, no old-palk precedent -> stock default
c_melt         = 0.5            ! 2.8.0-only, no old-palk precedent -> stock default
/

! MELT POND PARAMETERS - entirely new in 2.8.0, no &meltpond block existed in
! old palk_7's namelist.ice at all -> stock defaults throughout.
&meltpond
hi_min         = 0.10
hs1            = 0.03
pndaspect      = 0.80
rfracmin       = 0.15
rfracmax       = 1.00
albpnd         = 0.20
albpnd_frz     = 0.36
/
