
#include "CPP_OPTIONS.h"

#ifdef ENEA_COUPLER

C--  File rotate_wind.F: Routines to handle a vector coordinate system rotation.
C--   Contents
C--   o ROTATE_WIND_RL
C--   o ROTATE_WIND_RS

      subroutine rotate_wind_rl(
     U          uFldX, vFldY,
     U          uFldE, vFldN,
     I          xy2en, switchGrid, applyMask,  mythid
     &                     )

c     ==================================================================
c     SUBROUTINE rotate_wind_rl
c     ==================================================================
c
c     o uFldX/vFldY are in the model grid directions. 
c     o uFldE/vFldN are eastward/northward.
c     o This routine goes from uFldX/vFldY to uFldE/vFldN (for xy2en=.TRUE.) 
c         or vice versa (for xy2en=.FALSE.).
c     o uFldX/vFldY may be at the C grid velocity points, or at the A grid
c         velocity points (i.e. the C grid cell center). uFldE/vFldN are always 
c         at the cell center. If switchGrid=.TRUE. we go from C grid uFldX/vFldY
c         to A grid uFldE/vFldN, or vice versa. If switchGrid=.FALSE. we go
c         from A grid uFldX/vFldY to A grid uFldE/vFldN, or vice versa.
c     o If applyMask=.TRUE. then masks are applied to the output.
c     o In any case it is assumed that exchanges are done on the outside.
c
c     ==================================================================
c     SUBROUTINE rotate_wind_rl
c     ==================================================================

      implicit none

c     == global variables ==

#include "EEPARAMS.h"
#include "SIZE.h"
#include "PARAMS.h"
#include "GRID.h"

c     == routine arguments ==

      logical xy2en, switchGrid, applyMask
      _RL     uFldX(1-olx:snx+olx,1-oly:sny+oly,nsx,nsy)
      _RL     vFldY(1-olx:snx+olx,1-oly:sny+oly,nsx,nsy)
      _RL     uFldE(1-olx:snx+olx,1-oly:sny+oly,nsx,nsy)
      _RL     vFldN(1-olx:snx+olx,1-oly:sny+oly,nsx,nsy)

      integer mythid

c     == local variables ==

      integer bi,bj
      integer i,j,k
      _RL     tmpU(1-olx:snx+olx,1-oly:sny+oly)
      _RL     tmpV(1-olx:snx+olx,1-oly:sny+oly)
      CHARACTER*(MAX_LEN_MBUF) msgBuf

c     == end of interface ==

      do bj = mybylo(mythid),mybyhi(mythid)
       do bi = mybxlo(mythid),mybxhi(mythid)



        if ( xy2en ) then
c go from uFldX/vFldY to uFldE/vFldN
        if ( switchGrid ) then
C 1a) go from C grid velocity points to A grid velocity points
        do i = 1-olx,snx+olx
          tmpU(i,sny+Oly)=0.
          tmpV(i,sny+Oly)=0.
        enddo
        do j = 1-oly,sny+oly-1
          tmpU(snx+Olx,j)=0.
          tmpV(snx+Olx,j)=0.
        do i = 1-olx,snx+olx-1
          tmpU(i,j) = 0.5 _d 0
     &          *( uFldX(i+1,j,bi,bj) + uFldX(i,j,bi,bj) )
          tmpV(i,j) = 0.5 _d 0
     &          *( vFldY(i,j+1,bi,bj) + vFldY(i,j,bi,bj) )
          if (applyMask) then
            tmpU(i,j) = tmpU(i,j) * maskC(i,j,1,bi,bj)
            tmpV(i,j) = tmpV(i,j) * maskC(i,j,1,bi,bj)
          endif
          enddo
          enddo
        else
C 1b) stay at A grid velocity points (i.e. at the C grid cell center)
          do j = 1-oly,sny+oly
          do i = 1-olx,snx+olx
            tmpU(i,j) = uFldX(i,j,bi,bj)
            tmpV(i,j) = vFldY(i,j,bi,bj)
            if (applyMask) then
              tmpU(i,j) = tmpU(i,j) * maskC(i,j,1,bi,bj)
              tmpV(i,j) = tmpV(i,j) * maskC(i,j,1,bi,bj)
            endif
          enddo
          enddo
        endif!if ( switchGrid ) then

C 2) rotation
          do j = 1-oly,sny+oly
          do i = 1-olx,snx+olx
            uFldE(i,j,bi,bj) = 
     &         angleCosC(i,j,bi,bj)*tmpU(i,j)
     &        -angleSinC(i,j,bi,bj)*tmpV(i,j)
            vFldN(i,j,bi,bj) = 
     &         angleSinC(i,j,bi,bj)*tmpU(i,j)
     &        +angleCosC(i,j,bi,bj)*tmpV(i,j)
          enddo
          enddo

      else!if (xy2en) then
c go from uFldE/vFldN to uFldX/vFldY

C 1) rotation
          do j = 1-oly,sny+oly
          do i = 1-olx,snx+olx
            tmpU(i,j) = 
     &         angleCosC(i,j,bi,bj)*uFldE(i,j,bi,bj)
     &        +angleSinC(i,j,bi,bj)*vFldN(i,j,bi,bj)
            tmpV(i,j) =
     &        -angleSinC(i,j,bi,bj)*uFldE(i,j,bi,bj)
     &        +angleCosC(i,j,bi,bj)*vFldN(i,j,bi,bj)
          enddo
          enddo

        if ( switchGrid ) then
C 2a) go from A grid velocity points to C grid velocity points
          do i = 1-olx,snx+olx
            uFldX(i,1,bi,bj)=0.
            vFldY(i,1,bi,bj)=0.
          enddo
          do j = 1-oly+1,sny+oly
             uFldX(1,j,bi,bj)=0.
             vFldY(1,j,bi,bj)=0.
          do i = 1-olx+1,snx+olx
            uFldX(i,j,bi,bj) = 0.5 _d 0
     &         *( tmpU(i-1,j) + tmpU(i,j) )
            vFldY(i,j,bi,bj) = 0.5 _d 0
     &         *( tmpV(i,j-1) + tmpV(i,j) )
            if (applyMask) then
              uFldX(i,j,bi,bj)=uFldX(i,j,bi,bj)*maskW(i,j,1,bi,bj)
              vFldY(i,j,bi,bj)=vFldY(i,j,bi,bj)*maskS(i,j,1,bi,bj)
            endif
          enddo
          enddo
        else
C 2b) stay at A grid velocity points (i.e. at the C grid cell center)
          do j = 1-oly,sny+oly
          do i = 1-olx,snx+olx
            uFldX(i,j,bi,bj) = tmpU(i,j)
            vFldY(i,j,bi,bj) = tmpV(i,j)
            if (applyMask) then
              uFldX(i,j,bi,bj)=uFldX(i,j,bi,bj)*maskC(i,j,1,bi,bj)
              vFldY(i,j,bi,bj)=vFldY(i,j,bi,bj)*maskC(i,j,1,bi,bj)
            endif
          enddo
          enddo
        endif!if ( switchGrid ) then

        endif!if (xy2en) then

c        enddo
       enddo
      enddo

      return
      end


      subroutine rotate_wind_rs(
     U          uFldX, vFldY,
     U          uFldE, vFldN,
     I          xy2en, switchGrid, applyMask,  mythid
     &                     )


c     ==================================================================
c     SUBROUTINE rotate_wind_rs
c     ==================================================================
c
c     o uFldX/vFldY are in the model grid directions. 
c     o uFldE/vFldN are eastward/northward.
c     o This routine goes from uFldX/vFldY to uFldE/vFldN (for xy2en=.TRUE.) 
c         or vice versa (for xy2en=.FALSE.).
c     o uFldX/vFldY may be at the C grid velocity points, or at the A grid
c         velocity points (i.e. the C grid cell center). uFldE/vFldN are always 
c         at the cell center. If switchGrid=.TRUE. we go from C grid uFldX/vFldY
c         to A grid uFldE/vFldN, or vice versa. If switchGrid=.FALSE. we go
c         from A grid uFldX/vFldY to A grid uFldE/vFldN, or vice versa.
c     o If applyMask=.TRUE. then masks are applied to the output.
c     o In any case it is assumed that exchanges are done on the outside.
c
c     ==================================================================
c     SUBROUTINE rotate_wind_rs
c     ==================================================================

      implicit none

c     == global variables ==

#include "EEPARAMS.h"
#include "SIZE.h"
#include "PARAMS.h"
#include "GRID.h"

c     == routine arguments ==

      logical xy2en, switchGrid, applyMask
      _RS     uFldX(1-olx:snx+olx,1-oly:sny+oly,nsx,nsy)
      _RS     vFldY(1-olx:snx+olx,1-oly:sny+oly,nsx,nsy)
      _RS     uFldE(1-olx:snx+olx,1-oly:sny+oly,nsx,nsy)
      _RS     vFldN(1-olx:snx+olx,1-oly:sny+oly,nsx,nsy)

      integer mythid

c     == local variables ==

      integer bi,bj
      integer i,j,k
      _RS     tmpU(1-olx:snx+olx,1-oly:sny+oly)
      _RS     tmpV(1-olx:snx+olx,1-oly:sny+oly)
      CHARACTER*(MAX_LEN_MBUF) msgBuf

c     == end of interface ==

      do bj = mybylo(mythid),mybyhi(mythid)
       do bi = mybxlo(mythid),mybxhi(mythid)

        if ( xy2en ) then
c go from uFldX/vFldY to uFldE/vFldN
        if ( switchGrid ) then
C 1a) go from C grid velocity points to A grid velocity points
        do i = 1-olx,snx+olx
          tmpU(i,sny+Oly)=0.
          tmpV(i,sny+Oly)=0.
        enddo
        do j = 1-oly,sny+oly-1
          tmpU(snx+Olx,j)=0.
          tmpV(snx+Olx,j)=0.
        do i = 1-olx,snx+olx-1
          tmpU(i,j) = 0.5 _d 0
     &          *( uFldX(i+1,j,bi,bj) + uFldX(i,j,bi,bj) )
          tmpV(i,j) = 0.5 _d 0
     &          *( vFldY(i,j+1,bi,bj) + vFldY(i,j,bi,bj) )
          if (applyMask) then
            tmpU(i,j) = tmpU(i,j) * maskC(i,j,1,bi,bj)
            tmpV(i,j) = tmpV(i,j) * maskC(i,j,1,bi,bj)
          endif
          enddo
          enddo
        else
C 1b) stay at A grid velocity points (i.e. at the C grid cell center)
          do j = 1-oly,sny+oly
          do i = 1-olx,snx+olx
            tmpU(i,j) = uFldX(i,j,bi,bj)
            tmpV(i,j) = vFldY(i,j,bi,bj)
            if (applyMask) then
              tmpU(i,j) = tmpU(i,j) * maskC(i,j,1,bi,bj)
              tmpV(i,j) = tmpV(i,j) * maskC(i,j,1,bi,bj)
            endif
          enddo
          enddo
        endif!if ( switchGrid ) then

C 2) rotation
          do j = 1-oly,sny+oly
          do i = 1-olx,snx+olx
            uFldE(i,j,bi,bj) = 
     &         angleCosC(i,j,bi,bj)*tmpU(i,j)
     &        -angleSinC(i,j,bi,bj)*tmpV(i,j)
            vFldN(i,j,bi,bj) = 
     &         angleSinC(i,j,bi,bj)*tmpU(i,j)
     &        +angleCosC(i,j,bi,bj)*tmpV(i,j)
          enddo
          enddo

      else!if (xy2en) then
c go from uFldE/vFldN to uFldX/vFldY

C 1) rotation
          do j = 1-oly,sny+oly
          do i = 1-olx,snx+olx
            tmpU(i,j) = 
     &         angleCosC(i,j,bi,bj)*uFldE(i,j,bi,bj)
     &        +angleSinC(i,j,bi,bj)*vFldN(i,j,bi,bj)
            tmpV(i,j) =
     &        -angleSinC(i,j,bi,bj)*uFldE(i,j,bi,bj)
     &        +angleCosC(i,j,bi,bj)*vFldN(i,j,bi,bj)
          enddo
          enddo

        if ( switchGrid ) then
C 2a) go from A grid velocity points to C grid velocity points
          do i = 1-olx,snx+olx
            uFldX(i,1,bi,bj)=0.
            vFldY(i,1,bi,bj)=0.
          enddo
          do j = 1-oly+1,sny+oly
             uFldX(1,j,bi,bj)=0.
             vFldY(1,j,bi,bj)=0.
          do i = 1-olx+1,snx+olx
            uFldX(i,j,bi,bj) = 0.5 _d 0
     &         *( tmpU(i-1,j) + tmpU(i,j) )
            vFldY(i,j,bi,bj) = 0.5 _d 0
     &         *( tmpV(i,j-1) + tmpV(i,j) )
            if (applyMask) then
              uFldX(i,j,bi,bj)=uFldX(i,j,bi,bj)*maskW(i,j,1,bi,bj)
              vFldY(i,j,bi,bj)=vFldY(i,j,bi,bj)*maskS(i,j,1,bi,bj)
            endif
          enddo
          enddo
        else
C 2b) stay at A grid velocity points (i.e. at the C grid cell center)
          do j = 1-oly,sny+oly
          do i = 1-olx,snx+olx
            uFldX(i,j,bi,bj) = tmpU(i,j)
            vFldY(i,j,bi,bj) = tmpV(i,j)
            if (applyMask) then
              uFldX(i,j,bi,bj)=uFldX(i,j,bi,bj)*maskC(i,j,1,bi,bj)
              vFldY(i,j,bi,bj)=vFldY(i,j,bi,bj)*maskC(i,j,1,bi,bj)
            endif
          enddo
          enddo
        endif!if ( switchGrid ) then

        endif!if (xy2en) then

        enddo
       enddo
c      enddo

      return
      end

#endif
