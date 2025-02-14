
FC = gfortran
#FCFLAGS = `nf-config --fflags` -O0 -g -Wall -pedantic -fcheck=all -fbacktrace
FCFLAGS = `nf-config --fflags` -O3
LDFLAGS = `nf-config --flibs`

.SUFFIXES: .F90 .f90 .o

%.o: %.F90
	$(FC) $(FCFLAGS) -c $<

%.o: %.f90
	$(FC) $(FCFLAGS) -c $<

OBJS = types.o cfg_tools.o readwrite.o io_netcdf.o projection.o \
       mixed_grid.o domain.o

all :: create_coordinates

create_coordinates : create_coordinates.f90 $(OBJS)
	$(FC) $(FCFLAGS) -o $@ $< $(OBJS) $(LDFLAGS)

clean :
	rm -f create_coordinates $(OBJS) *.mod

types.o : types.f90
io_netcdf.o : io_netcdf.f90
cfg_tools.o : cfg_tools.f90 readwrite.o projection.o
readwrite.o : readwrite.f90 io_netcdf.o
projection.o : projection.f90 readwrite.o
mixed_grid.o : mixed_grid.f90 readwrite.o
domain.o : domain.f90 readwrite.o readwrite.o mixed_grid.o
