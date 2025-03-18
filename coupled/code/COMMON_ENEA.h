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
      INTEGER, PARAMETER :: IG_BEGIN_ATLANTIC = 64
#endif

cgmMASK(
      COMMON /SURF_MASK/ EmPmR_msk, EmPmR_SALT_msk
      _RL        EmPmR_msk(1-OLx:sNx+OLx,1-OLy:sNy+OLy,nSx,nSy)
      _RL   EmPmR_SALT_msk(1-OLx:sNx+OLx,1-OLy:sNy+OLy,nSx,nSy)
cgmMASK)
