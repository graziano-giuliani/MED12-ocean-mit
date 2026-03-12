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
      INTEGER, PARAMETER :: IG_BEGIN_BLACKSEA = 450
      INTEGER, PARAMETER :: JG_BEGIN_BLACKSEA = 170
#endif
