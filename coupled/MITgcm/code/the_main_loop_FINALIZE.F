#include "PACKAGES_CONFIG.h"
#include "CPP_OPTIONS.h"
#ifdef ALLOW_AUTODIFF
# include "AUTODIFF_OPTIONS.h"
#endif
#ifdef ALLOW_GENERIC_ADVDIFF
# include "GAD_OPTIONS.h"
#endif
#ifdef ALLOW_GGL90
# include "GGL90_OPTIONS.h"
#endif
#ifdef ALLOW_GMREDI
# include "GMREDI_OPTIONS.h"
#endif
#ifdef ALLOW_OBCS
# include "OBCS_OPTIONS.h"
#endif
#ifdef ALLOW_SEAICE
# include "SEAICE_OPTIONS.h"
#endif
#ifdef ALLOW_SALT_PLUME
# include "SALT_PLUME_OPTIONS.h"
#endif
#ifdef ALLOW_GCHEM
# include "GCHEM_OPTIONS.h"
#endif
#ifdef ALLOW_DIC
# include "DIC_OPTIONS.h"
#endif
#ifdef ALLOW_BLING
# include "BLING_OPTIONS.h"
#endif
#ifdef ALLOW_EXF
# include "EXF_OPTIONS.h"
#endif
#ifdef ALLOW_STREAMICE
# include "STREAMICE_OPTIONS.h"
#endif
#ifdef ALLOW_SHELFICE
# include "SHELFICE_OPTIONS.h"
#endif
#ifdef ALLOW_COST
# include "COST_OPTIONS.h"
#endif
#ifdef ALLOW_CTRL
# include "CTRL_OPTIONS.h"
#endif
#ifdef ALLOW_ECCO
# include "ECCO_OPTIONS.h"
#endif
#ifdef ALLOW_PROFILES
# include "PROFILES_OPTIONS.h"
#endif
#ifdef ALLOW_RBCS
# include "RBCS_OPTIONS.h"
#endif

#ifdef ENEA_COUPLER
!BOP
!     !ROUTINE: THE_MAIN_LOOP
!     !INTERFACE:
      SUBROUTINE THE_MAIN_LOOP_FINALIZE( myTime, myIter, myThid )

!     !DESCRIPTION: \bv
!     *================================================================*
!     | SUBROUTINE the_main_loop
!     | o Run the ocean model and evaluate the specified cost function.
!     *================================================================*
!     | THE_MAIN_LOOP is the toplevel routine for the Transformation of
!     | Algorithm in Fortran (TAF).
!     | For this purpose the initialization of the model was split into
!     | two parts. Variables that are kept independent of control
!     | parameters (e.g. horizontal grid dxC, etc.) are set in
!     | INITIALISE_FIXED, whereas variables that can (potentially) be
!     | modified by control parameters (e.g. initial temperature and
!     | salinity) are initialized in INITIALISE_VARIA.
!     *================================================================*
!     \ev

!     !USES:
      IMPLICIT NONE
!     == Global variables ==
#include "SIZE.h"
#include "EEPARAMS.h"
#include "PARAMS.h"

!**************************************
#ifdef ALLOW_AUTODIFF
# ifndef ALLOW_OPENAD

! These includes are needed for
! AD-checkpointing.
! They provide the fields to be stored.

#  include "GRID.h"
#  include "DYNVARS.h"
#  include "SURFACE.h"
#  include "FFIELDS.h"
#  include "EOS.h"
#  include "AUTODIFF.h"

#  ifdef ALLOW_GENERIC_ADVDIFF
#   include "GAD.h"
#   include "GAD_SOM_VARS.h"
#  endif
#  ifdef ALLOW_MOM_FLUXFORM
#   include "MOM_FLUXFORM.h"
#  endif
#  ifdef ALLOW_CD_CODE
#   include "CD_CODE_VARS.h"
#  endif
#  ifdef ALLOW_PTRACERS
#   include "PTRACERS_SIZE.h"
#   include "PTRACERS_FIELDS.h"
#   include "PTRACERS_START.h"
#  endif
#  ifdef ALLOW_GCHEM
#   include "GCHEM_SIZE.h"
#   include "GCHEM_FIELDS.h"
#  endif
#  ifdef ALLOW_CFC
#   include "CFC.h"
#  endif
#  ifdef ALLOW_DIC
#   include "DIC_VARS.h"
#   include "DIC_LOAD.h"
#   include "DIC_ATMOS.h"
#   include "DIC_CTRL.h"
#   include "DIC_COST.h"
#  endif
#  ifdef ALLOW_OBCS
#   include "OBCS_PARAMS.h"
#   include "OBCS_FIELDS.h"
#   include "OBCS_SEAICE.h"
#   ifdef ALLOW_PTRACERS
#    include "OBCS_PTRACERS.h"
#   endif
#  endif
#  ifdef ALLOW_EXF
#   ifdef ALLOW_BULKFORMULAE
#    include "EXF_CONSTANTS.h"
#   endif
#   include "EXF_INTERP_SIZE.h"
#   include "EXF_FIELDS.h"
#  endif /* ALLOW_EXF */
#  ifdef ALLOW_BLING
#   include "BLING_VARS.h"
#   include "BLING_LOAD.h"
#  endif
#  ifdef ALLOW_SEAICE
#   include "SEAICE_SIZE.h"
#   include "SEAICE.h"
#   include "SEAICE_PARAMS.h"
#   include "SEAICE_COST.h"
#   include "SEAICE_TRACER.h"
#  endif
#  ifdef ALLOW_SALT_PLUME
#   include "SALT_PLUME.h"
#  endif
#  ifdef ALLOW_THSICE
#   include "THSICE_SIZE.h"
#   include "THSICE_VARS.h"
#   include "THSICE_COST.h"
#  endif
#  ifdef ALLOW_SHELFICE
#   include "SHELFICE.h"
#   include "SHELFICE_COST.h"
#  endif
#  ifdef ALLOW_STREAMICE
#   include "STREAMICE.h"
#   include "STREAMICE_ADV.h"
#   include "STREAMICE_BDRY.h"
#   include "STREAMICE_CG.h"
#  endif
#  ifdef ALLOW_EBM
#   include "EBM.h"
#  endif
#  ifdef ALLOW_RBCS
#   include "RBCS_SIZE.h"
#   include "RBCS_FIELDS.h"
#  endif
#  ifdef ALLOW_OFFLINE
#   include "OFFLINE.h"
#  endif
# if (defined ALLOW_CG2D_NSA || defined NONLIN_FRSURF || defined ALLOW_DEPTH_CONTROL)
#   include "CG2D.h"
#  endif
#  ifdef ALLOW_DIVIDED_ADJOINT
#   ifdef ALLOW_USE_MPI
#    include "mpif.h"
#   endif
#  endif

!-- keep tamc.h here without ALLOW_AUTODIFF_TAMC for ALLOW_TAMC_CHECKPOINTING
#  include "tamc.h"

#  ifdef ALLOW_GGL90
#   include "GGL90.h"
#  endif
#  ifdef ALLOW_PROFILES
#   include "PROFILES_SIZE.h"
#   include "profiles.h"
#  endif
#  ifdef ALLOW_ECCO
#   include "ecco_cost.h"
#  endif
!     it is important that this file is included after SEAICE_SIZE.h
#  include "AUTODIFF_STORE.h"
# endif /* undef ALLOW_OPENAD */

# ifdef ALLOW_CTRL
# include "CTRL_SIZE.h"
# include "CTRL.h"
# include "CTRL_DUMMY.h"
# include "CTRL_GENARR.h"
# include "CTRL_OBCS.h"
# endif
# ifdef ALLOW_COST
#  include "cost.h"
# endif

#endif /* ALLOW_AUTODIFF */

#ifdef ALLOW_TAPENADE
# ifdef ALLOW_GMREDI
#  include "GMREDI.h"
#  include "GMREDI_TAVE.h"
# endif
# ifdef ALLOW_KPP
#  include "KPP.h"
!#  include "KPP_PARAMS.h"
# endif
# ifdef ALLOW_TIMEAVE
#  include "TIMEAVE_STATV.h"
# endif
# ifdef ALLOW_EXF
#  include "EXF_PARAM.h"
#  include "EXF_INTERP_PARAM.h"
# endif
# ifdef ALLOW_DOWN_SLOPE
#  include "DWNSLP_SIZE.h"
#  include "DWNSLP_VARS.h"
# endif
# ifdef ALLOW_PTRACERS
#  include "PTRACERS_PARAMS.h"
# endif
#endif /* ALLOW_TAPENADE */

!**************************************

!     !INPUT/OUTPUT PARAMETERS:
!     == Routine arguments ==
!     note: under the multi-threaded model myIter and
!           myTime are local variables passed around as routine
!           arguments. Although this is fiddly it saves the need to
!           impose additional synchronisation points when they are
!           updated.
!     myTime :: time counter for this thread
!     myIter :: iteration counter for this thread
!     myThid :: thread number for this instance of the routine.
      _RL     myTime
      INTEGER myIter
      INTEGER myThid

!     !FUNCTIONS:
!     == Functions ==

!     !LOCAL VARIABLES:
!     == Local variables ==
      INTEGER iloop
#ifdef STORE_LOADEDREC_TEST
      INTEGER bi,bj
#endif /* STORE_LOADEDREC_TEST */
#ifdef ALLOW_AUTODIFF
# ifdef ALLOW_TAMC_CHECKPOINTING
      INTEGER ilev_1
      INTEGER ilev_2, max_lev2
#  ifndef AUTODIFF_2_LEVEL_CHECKPOINT
      INTEGER ilev_3, max_lev3
#  endif
#  ifdef AUTODIFF_4_LEVEL_CHECKPOINT
      INTEGER ilev_4, max_lev4
#  endif
# endif /* ALLOW_TAMC_CHECKPOINTING */
#endif /* ALLOW_AUTODIFF */
!EOP

#ifdef ALLOW_ECCO
!--     Accumulate time averages of temperature, salinity
      CALL TIMER_START('COST_AVERAGESFIELDS [THE_MAIN_LOOP]',myThid)
      CALL COST_AVERAGESFIELDS( endtime, myThid )
      CALL TIMER_STOP ('COST_AVERAGESFIELDS [THE_MAIN_LOOP]',myThid)
#endif /* ALLOW_ECCO */

#ifdef ALLOW_PROFILES
      IF ( usePROFILES ) THEN
!--   Accumulate in-situ time averages of temperature, salinity, SSH.
        CALL TIMER_START('PROFILES_INLOOP    [THE_MAIN_LOOP]', myThid)
        CALL PROFILES_INLOOP( endtime, myThid )
        CALL TIMER_STOP ('PROFILES_INLOOP    [THE_MAIN_LOOP]', myThid)
!--   Compute all profiles cost function contributions.
        CALL PROFILES_COST( myIter, myTime, myThid )
      ENDIF
#endif

#ifdef ALLOW_ECCO
      IF ( useECCO ) then
!--   Compute all ecco cost function contributions.
        CALL TIMER_START('ECCO_COST_DRIVER   [THE_MAIN_LOOP]', myThid)
        CALL ECCO_COST_DRIVER ( endTime, myIter, myThid )
        CALL TIMER_STOP ('ECCO_COST_DRIVER   [THE_MAIN_LOOP]', myThid)
      ENDIF
#endif /* ALLOW_ECCO */

#ifdef ALLOW_COST
!--   Sum all cost function contributions.
      CALL TIMER_START('COST_FINAL         [ADJOINT SPIN-DOWN]', myThid)
      CALL COST_FINAL ( myThid )
      CALL TIMER_STOP ('COST_FINAL         [ADJOINT SPIN-DOWN]', myThid)

# ifdef ALLOW_OPENAD
!$openad DEPENDENT(fc)
# endif /* ALLOW_OPENAD */

#endif /* ALLOW_COST */

#ifdef USE_PDAF
!     PDAF finalization
      CALL FINALIZE_PDAF( )
#endif

      _BARRIER
      CALL TIMER_STOP ('MAIN LOOP           [THE_MAIN_LOOP]', myThid)

#ifdef ALLOW_DEBUG
      IF (debugMode) CALL DEBUG_LEAVE('THE_MAIN_LOOP',myThid)
#endif

      RETURN
      END
#endif
