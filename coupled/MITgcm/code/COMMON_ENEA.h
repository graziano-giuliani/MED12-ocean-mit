CBOP
C    !ROUTINE: COMMON_ENEA.h
C    !INTERFACE:
C    include COMMON_ENEA.h
C    !DESCRIPTION: \bv
C     *==========================================================*
C     | o Header file defining masks required for coupling
C     *==========================================================*
C     \ev
CEOP

#ifdef MED_12_ATLANTIC
      INTEGER, PARAMETER :: IG_BEGIN_ATLANTIC_RELAX  = 1
      INTEGER, PARAMETER :: IG_END_ATLANTIC_RELAX    = 32
      INTEGER, PARAMETER :: IG_BEGIN_ATLANTIC_BUFFER = 33
      INTEGER, PARAMETER :: IG_END_ATLANTIC_BUFFER   = 65
C     STORAGE TO KEEP THE REMOVED MEAN OVER THE BUFFER ZONE
      COMMON /ENEA_MED_BUFFER/ med12_buffer
      _RL med12_buffer(1-OLx:sNx+OLx,1-OLy:sNy+OLy,nSx,nSy)
#endif
