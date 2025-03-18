CBOI
C
C   SUBROUTINE PTREENTRY OUT OF MAIN FOR COUPLING
C 
CEOI

C--   Get C preprocessor options
#include "PACKAGES_CONFIG.h"
#include "CPP_OPTIONS.h"

#ifdef ENEA_COUPLER

C---+----1----+----2----+----3----+----4----+----5----+----6----+----7-|--+----|

CBOP 0
C     !ROUTINE: PTREENTRY

C     !INTERFACE:
      SUBROUTINE PTREENTRY(
     I     myThid )

C     !DESCRIPTION:
C     Re-entry point for a pthreads-based threading mechanism.  The
C     intent is to produce a threading hack that will work with gcc/g77.

C     !USES:
      IMPLICIT NONE
#include "SIZE.h"
#include "EEPARAMS.h"
#include "EESUPPORT.h"
#include "PARAMS.h"
#include "GRID.h"
#include "DYNVARS.h"
#include "FFIELDS.h"
#include "SURFACE.h"

C     !INPUT PARAMETERS:
C     myThid       :: my thread Id number
      INTEGER myThid
CEOP

      WRITE(*,*) 'myThid = ', myThid
      CALL CHECK_THREADS( myThid )

c     CALL THE_MODEL_MAIN(myThid)

      threadIsComplete(myThid) = .TRUE.

      RETURN
      END

C---+----1----+----2----+----3----+----4----+----5----+----6----+----7-|--+----|

#endif
