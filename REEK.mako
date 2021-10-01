<%!
import numpy as np
import datetime as dt
%>
-- *------------------------------------------*
-- *                                          *
-- * base grid model with input parameters    *
-- *                                          *
-- *------------------------------------------*

-- *****************************************************
RUNSPEC
-- *****************************************************

PATHS
 'ECLINC' './include' /
/
-- Simulation run title
TITLE
Reservoir Simulation Model Building Basic Principles - Generic Reservoir

NOECHO

--
-- ----------------------------------------------------
-- Simulation grid dimension (Imax, Jmax, Kmax)
DIMENS
    40  64   14  /

--
-- ----------------------------------------------------
-- Simulation run start
START
 1 DEC 1999 /

--
-- ----------------------------------------------------
--Activate "Data Check Only" option
--NOSIM
--
--

--
-- ----------------------------------------------------
-- Fluid phases present
OIL
GAS
WATER
DISGAS
VAPOIL

--
-- ----------------------------------------------------
-- Measurement unit used
METRIC

--
-- ----------------------------------------------------
--Options to process grid data
--If MULTX-, MULTY- and MULTZ- are used, set first parameter= 'YES'
GRIDOPTS
-- MULTNUM?   NRMULT
   'NO'      1*       /

--
-- ----------------------------------------------------
--Use saturation table end-point scaling
ENDSCALE
 'NODIR'  'REVERS'  1  20  /

--
-- ----------------------------------------------------
--Options for equilibration
EQLOPTS
 'QUIESC'  /

--
-- ----------------------------------------------------
--
--Table dimensions
TABDIMS
-- NTSFUN NTPVT NSSFUN NPPVT NTFIP NRPVT
     1      1     30    24    10    20   /
--
-- ----------------------------------------------------
-- Dimensions for equilibration tables
EQLDIMS
  2  100  20  /
--
-- ----------------------------------------------------
--Regions dimension data
REGDIMS
-- NTFIP NMFIPR NRFREG NTFREG
    2    2      0      3      /
--
-- ----------------------------------------------------
--Dimensions for fault data
FAULTDIM
  1300  /

--
-- ----------------------------------------------------
--Dimension for well data
WELLDIMS
 230  120 50 80 /

--
-- ----------------------------------------------------
--Production well VFP table dimension
VFPPDIMS
  20  20  15  15  15   50  /

--
-- ----------------------------------------------------
-- If injection well VFP data is required, 
-- they should be specified here first
VFPIDIMS
  10   2   5  /

--
-- ----------------------------------------------------
--Dimensions and options for tracers
--TRACERS
--NOTRAC NWTRAC NGTRAC NETRAC DIFF/NODIFF
--    0     3     0    0    'NODIFF'      /

--
-- ----------------------------------------------------
--Summary file dimensions
SMRYDIMS
  15000  /
--

-- ----------------------------------------------------
-- Input and output files format
--UNIFIN
--UNIFOUT

--FMTOUT




-- *************************************************************************
-- In this section simulation grid and static reservoir parameters are given
-- *************************************************************************

GRID 

-- ****************************************************
-------------------------------------------------------

--
--Disable echoing of the input file  
NOECHO

--
--Requests output of an INIT file
INIT

--
--Control output of the Grid geometry file
GRIDFILE
  2 1  /

--Message print and stop limits
MESSAGES
 3* 1000 4* 1000000 1000 /

--
--Generates connections across pinched-out layers
PINCH
 0.4  NOGAP  1*  TOPBOT  TOP  /

--
--Grid data unit
GRIDUNIT
  METRES  /

--
--Input of pre-processor map origin (X1, Y1, X2, Y2, X3, Y3)
--X1 Y1 The X and Y coordinates of one point of the grid Y-axis relative to the map
--X2 Y2 The X and Y coordinates of the grid origin relative to the map origin
--X3 Y3 The X and Y coordinates of one point of the grid X-axis relative to the map
MAPAXES
 0.0 100.0 0.0 0.0 100.0 0.0  /
--
--

NOECHO

--
-- ----------------------------------------------------
--Include simulation grid
INCLUDE
  '$ECLINC/example_grid_sim.GRDECL' /

--
-- ----------------------------------------------------
--Include ACTNUM data, if any
--INCLUDE
--  '../Include/example_actnum_sim.GRDECL' /
--

-- ----------------------------------------------------
-- Remove blocks in the water zone
-- The next row of blocks are used tor aquifer modelling

BOX
  1 8  1 64   1 14 /

ACTNUM
 7168*0 /

ENDBOX

-- ----------------------------------------------------


-- ----------------------------------------------------
--Include FLUXNUM regions
INCLUDE
  '$ECLINC/example_fluxnum_sim.GRDECL' /

--
-- ---------------------------------------------------
-- Include faults
-- Make sure that faults' name have 8 characters max.
INCLUDE
  '$ECLINC/example_faults_sim.GRDECL'  /


-- ---------------------------------------------------
-- Porosity and permeabiliy:
-- ---------------------------------------------------
--Include porosity
--INCLUDE
 --'$ECLINC/example_poro.GRDECL'  /

-- If you want to add uncertainty in the PORO, add the line below and comment the one above
-- '../priors/poro/PORO_0'/

PORO
% for it in poro:
${it}
% endfor
/
--
-- ---------------------------------------------------
--Include X-direction permeability
--INCLUDE
--'$ECLINC/example_permx.GRDECL'  / 

PERMX
% for it in permx:
${it}
% endfor
/


-- ---------------------------------------------------
-- Copy PERMX to PERMY  & PERMZ 
COPY
 PERMX   PERMY   /
 PERMX   PERMZ   /
/
--
-- ---------------------------------------------------
-- Set Kv/Kh 
MULTIPLY
 PERMZ   0.3     /
/


-- ---------------------------------------------------
-- Include MULTZ values for barriers here:
--

-- ---------------------------------------------------
-- Fault seal

--INCLUDE
--'$ECLINC/fault_seal.inc' /
-- If you want to add uncertainty to faults, add line below and comment the one above
--'../priors/multflt/multflt_0'


MULTFLT
<%
tmp = ['F7', 'F2', 'F3', 'F4', 'F5', 'F6']
%>
% for index, it in enumerate(multflt):
${'{} {} /'.format(tmp[index], it)}
% endfor
/

-- ***************************************************
-- In this section simulation grid parameters are edited
-- ***************************************************

EDIT

-- ***************************************************


-- ---------------------------------------------------
-- The pore volume of a row of blocks is increased
-- to model the effect of the aquifer:
INCLUDE
 '$ECLINC/aquifer.inc'  /




-- ***************************************************
-- In this section fluid-rock properties and 
-- relative permabilities are given
-- ***************************************************

PROPS

-- ***************************************************

-- ---------------------------------------------------
-- Relative permeability endpints
--

INCLUDE
 '$ECLINC/endpoints.inc' /


--
-- ---------------------------------------------------
-- In this example SWCR(critical water saturation) = SWL (connate water saturation) 
COPY
 SWL   SWCR  / 
 SWL   SGU   /  
/

--
-- ---------------------------------------------------
-- Next 2 keywords are used to make maximum gas saturation consistent: SGU=1-SWL
-- 
MULTIPLY
 SGU   -1 /
/
ADD
 SGU    1  /
/

--
-- ---------------------------------------------------
-- Include relative perm data:
INCLUDE
 '$ECLINC/example_relperm.relperm'   /

-- ---------------------------------------------------
-- Hysteresis parameters and model selection
--EHYSTR
--0.07 0 1.0     /

-- ---------------------------------------------------
-- Include PVT data
INCLUDE
 '$ECLINC/example_pvt.txt' /






-- ***********************************************************
-- In this section simulation grid region parameters are given
-- ***********************************************************

REGIONS

-- ***************************************************

-- ---------------------------------------------------
-- Region parameters, SATNUM, PVTNUM, etc.
-- In this example: 
-- only 1 PVTNUM, 1 SATNUM, 2 FIPNUM for entire grid
-- PVTNUM & SATNUM are defined in this file
-- FIPNUM & FLUXNUM are imported from files
-- Normally these parameters are established using RMS
--


-- ---------------------------------------------------
--Include EQLNUM regions
INCLUDE
 '$ECLINC/example_eqlnum.GRDECL' /


EQUALS
 SATNUM     1       /
 PVTNUM     1      /   
/

--
-- ---------------------------------------------------
--Include FIPNUM data
-- 1) can be imported if available 
INCLUDE
  '$ECLINC/example_fipnum.GRDECL'  /








--
--
-- ***************************************************
-- In this section the initialization parameters aand
-- dynamic parameters are defined
-- ***************************************************

SOLUTION

-- ***************************************************


------------------------------------------------------
--
--Simulation model initialisation data
--
--   DATUM  DATUM   OWC     OWC    GOC    GOC    RSVD   RVVD   SOLN
--   Depth  Pres.   Depth   Pcow   Depth  Pcog   Table  Table  Method
EQUIL
     2469   382.4   1705.0  0.0    500    0.0     1     1      20 / 
     2469   382.4   1000.0  0.0    500    0.0     1     1      20 /       
    

--
-- ---------------------------------------------------
-- Vaporized oil-gas ratio versus depth, one for each 
-- equilibration region
--
RVVD
 2000   0.0
 4000   0.0   /
 2000   0.0
 4000   0.0   / 


--
-- ---------------------------------------------------
-- Dissolved gas-oil ratio versus depth, 

RSVD
 1500 184.0
 4000 184.0  /
 1500 184.0
 4000 184.0  /
 
-- ---------------------------------------------------
-- Oil vaporization control
--
--VAPPARS
-- 2  0.1  /


-- ---------------------------------------------------
-- Controls on output from SOLUTION section
RPTSOL
 RESTART=2 THPRES FIP=2   /


-- ---------------------------------------------------
--Controls on output to the RESTART file
RPTRST
 ALLPROPS=2 BASIC=2 FIP  /




--
-- **************************************************************************************
-- In this section simulation output data to be written to summary file are defined
-- **************************************************************************************

SUMMARY

-- ***************************************************


-- ---------------------------------------------------
-- Summary data to be written to summary file
--
-- Outputs the date to the summary file
DATE

RPTONLY

INCLUDE
 '$ECLINC/example_summary.txt'   /

-- RPTSMRY
-- 0 /
--
--
-- **************************************************************************************
-- In this section data required to describe history and prediction is given
-- - well completions, well production/injection, well constraints
-- - platform/production unit constraints, etc.
-- **************************************************************************************

SCHEDULE

-- ***************************************************

NOECHO

TUNING
 1.0 14.0 7* 1.0 /
 /
 /


-- ---------------------------------------------------
-- Schedule file with allocated rates 
--

RPTSCHED
   RESTART=2 /

--update drilling sequence here
WELSPECS
% for well in name:
% if well== 'OP_1':
${"  {}       'OP'   31   37  1*       'OIL'  7* /".format(well)}
% elif well == 'OP_2':
${"  {}       'OP'   20   51  1*       'OIL'  7*/".format(well)}
% elif well== 'OP_3':
${"  {}       'OP'   31   18  1*       'OIL'  7*/".format(well)}
% elif well == 'OP_4':
${"  {}        'OP'   20   37  1*       'OIL'  7* /".format(well)}
% elif well== 'OP_5':
${"  {}       'OP'   27   29  1*       'OIL'  7*/".format(well)}
% elif well == 'WI_1':
${"  {}       'WI'   15   28  1*       'WATER'  7* /".format(well)}
% elif well == 'WI_2':
${"  {}       'WI'   33   54  1*       'WATER'  7* /".format(well)}
% elif well == 'WI_3':
${"  {}       'WI'    18   57  1*       'WATER'  7* /".format(well)}
% endif
% endfor

/

--define the ordering of well connections

COMPORD
'OP_4'    INPUT /
'OP_3'    INPUT /
'WI_1'    INPUT /
'WI_2'    INPUT /
'WI_3'    INPUT /
'OP_1'    INPUT /
'OP_2'    INPUT /
'OP_5'    INPUT /
/


COMPDAT 
-- WELL        I    J    K1  K2            Sat.        CF       DIAM        KH SKIN ND        DIR   Ro 
-------------------------------------------------------------------------------------------------------------
     'OP_1'   31   37    1    1      'OPEN'  1*     32.948      0.311   3047.839  2*         'X'     22.100 /
     'OP_1'   31   37    2    2      'OPEN'  1*     46.825      0.311   4332.346  2*         'X'     22.123 /
     'OP_1'   31   37    3    3      'OPEN'  1*     51.867      0.311   4799.764  2*         'X'     22.143 /
     'OP_1'   31   37    4    4      'OPEN'  1*     34.243      0.311   3169.482  2*         'X'     22.166 /
     'OP_1'   31   37    5    5      'OPEN'  1*     36.435      0.311   3375.309  2*         'X'     22.262 /
     'OP_1'   31   37    6    6      'OPEN'  1*     39.630      0.311   3672.067  2*         'X'     22.283 /
     'OP_1'   31   37    7    7      'OPEN'  1*     33.975      0.311   3148.671  2*         'X'     22.307 /
     'OP_1'   31   37    8    8      'OPEN'  1*     24.869      0.311   2305.242  2*         'X'     22.329 /
     'OP_1'   31   37    9    9      'OPEN'  1*     38.301      0.311   3551.043  2*         'X'     22.351 /
     'OP_1'   31   37   10   10      'OPEN'  1*      6.642      0.311    615.914  2*         'X'     22.372 /
     'OP_1'   31   37   11   11      'OPEN'  1*      1.322      0.311    122.614  2*         'X'     22.396 /
     'OP_1'   31   37   12   12      'OPEN'  1*      3.797      0.311    352.293  2*         'X'     22.418 /
     'OP_1'   31   37   13   13      'OPEN'  1*     14.742      0.311   1367.872  2*         'X'     22.439 /
     'OP_1'   31   37   14   14      'OPEN'  1*     19.731      0.311   1831.202  2*         'X'     22.463 /
-------------------------------------------------------------------------------------------------------------     
     'OP_2'   20   51    1    1      'OPEN'  1*      1.168      0.311    107.872  2*         'Y'     21.925 /
     'OP_2'   20   51    2    2      'OPEN'  1*     15.071      0.311   1391.859  2*         'Y'     21.920 /
     'OP_2'   20   51    3    3      'OPEN'  1*      6.242      0.311    576.458  2*         'Y'     21.915 /
     'OP_2'   20   51    4    4      'OPEN'  1*     16.493      0.311   1522.982  2*         'Y'     21.908 /
     'OP_2'   20   51    5    5      'OPEN'  1*      7.359      0.311    679.489  2*         'Y'     21.903 /
-------------------------------------------------------------------------------------------------------------       
     'OP_3'   31   18    1    1      'OPEN'  1*     27.412      0.311   2445.337  2*         'Y'     18.521 /
     'OP_3'   31   18    2    2      'OPEN'  1*     55.195      0.311   4923.842  2*         'Y'     18.524 /
     'OP_3'   31   18    3    3      'OPEN'  1*     18.032      0.311   1608.615  2*         'Y'     18.526 /
     'OP_3'   31   18    4    4      'OPEN'  1*     56.817      0.311   5047.177  2*         'Y'     18.155 /
     'OP_3'   31   18    5    5      'OPEN'  1*      4.728      0.311    420.067  2*         'Y'     18.162 /
-------------------------------------------------------------------------------------------------------------       
     'OP_4'   20   37    1    1      'OPEN'  1*      8.163      0.311    795.338  2*         'Z'     28.779 /
     'OP_4'   20   37    2    2      'OPEN'  1*      7.916      0.311    771.108  2*         'Z'     28.747 /
     'OP_4'   20   37    3    3      'OPEN'  1*     10.755      0.311   1047.473  2*         'Z'     28.714 /
     'OP_4'   20   37    4    4      'OPEN'  1*     21.207      0.311   2064.890  2*         'Z'     28.680 /
     'OP_4'   20   37    5    5      'OPEN'  1*     26.941      0.311   2622.591  2*         'Z'     28.648 /
     'OP_4'   20   37    6    6      'OPEN'  1*     11.968      0.311   1164.811  2*         'Z'     28.615 /
     'OP_4'   20   37    7    7      'OPEN'  1*     16.366      0.311   1592.462  2*         'Z'     28.582 /
 -------------------------------------------------------------------------------------------------------------      
     'OP_5'   27   29    1    1      'OPEN'  1*     58.626      0.311   5516.231  2*         'Z'     24.063 /
     'OP_5'   27   29    2    2      'OPEN'  1*     55.544      0.311   5226.470  2*         'Z'     24.068 /
     'OP_5'   27   29    3    3      'OPEN'  1*     50.324      0.311   4735.625  2*         'Z'     24.077 /
     'OP_5'   27   29    4    4      'OPEN'  1*     44.385      0.311   4177.145  2*         'Z'     24.088 /
     'OP_5'   27   29    5    5      'OPEN'  1*     24.270      0.311   2284.220  2*         'Z'     24.095 /
     'OP_5'   27   29    6    6      'OPEN'  1*      8.814      0.311    829.641  2*         'Z'     24.105 /
-------------------------------------------------------------------------------------------------------------  
     'WI_1'   15   28    1    1      'OPEN'  1*      5.909      0.311    563.885  2*         'Z'     25.854 /
     'WI_1'   15   28    2    2      'OPEN'  1*      4.847      0.311    462.523  2*         'Z'     25.838 /
     'WI_1'   15   28    3    3      'OPEN'  1*      0.667      0.311     63.667  2*         'Z'     25.825 /
     'WI_1'   15   28    4    4      'OPEN'  1*      6.223      0.311    593.705  2*         'Z'     25.810 /
     'WI_1'   15   28    5    5      'OPEN'  1*      3.189      0.311    304.229  2*         'Z'     25.794 /
     'WI_1'   15   28    6    6      'OPEN'  1*      0.157      0.311     14.955  2*         'Z'     25.785 /
     'WI_1'   15   28    7    7      'OPEN'  1*      0.364      0.311     34.694  2*         'Z'     25.753 /
     'WI_1'   15   28    8    8      'OPEN'  1*      0.364      0.311     34.694  2*         'Z'     25.753 /
     'WI_1'   15   28    9    9      'OPEN'  1*      4.948      0.311    471.758  2*         'Z'     25.740 /
     'WI_1'   15   28   10   10      'OPEN'  1*      5.721      0.311    545.448  2*         'Z'     25.726 /
     'WI_1'   15   28   11   11      'OPEN'  1*     21.704      0.311   2069.027  2*         'Z'     25.711 /
     'WI_1'   15   28   12   12      'OPEN'  1*     26.860      0.311   2560.268  2*         'Z'     25.697 /
     'WI_1'   15   28   13   13      'OPEN'  1*     17.598      0.311   1677.218  2*         'Z'     25.682 /
     'WI_1'   15   28   14   14      'OPEN'  1*      0.391      0.311     37.238  2*         'Z'     25.672 /
-------------------------------------------------------------------------------------------------------------  
     'WI_2'   33   55    1    1      'OPEN'  1*     29.166      0.311   2557.130  2*         'Y'     17.063 /
     'WI_2'   33   55    2    2      'OPEN'  1*     62.350      0.311   5467.790  2*         'Y'     17.081 /
     'WI_2'   33   55    3    3      'OPEN'  1*     53.736      0.311   4713.503  2*         'Y'     17.100 /
     'WI_2'   33   55    4    4      'OPEN'  1*     29.247      0.311   2565.989  2*         'Y'     17.117 /
     'WI_2'   33   55    5    5      'OPEN'  1*     58.798      0.311   5159.877  2*         'Y'     17.136 /
     'WI_2'   33   55    6    6      'OPEN'  1*     69.803      0.311   6126.899  2*         'Y'     17.154 /
     'WI_2'   33   55    7    7      'OPEN'  1*     56.547      0.311   4964.561  2*         'Y'     17.172 /
     'WI_2'   33   55    8    8      'OPEN'  1*     42.880      0.311   3765.444  2*         'Y'     17.190 /
     'WI_2'   33   55    9    9      'OPEN'  1*     42.339      0.311   3718.758  2*         'Y'     17.208 /
     'WI_2'   33   55   10   10      'OPEN'  1*     21.881      0.311   1922.350  2*         'Y'     17.226 /
     'WI_2'   33   55   11   11      'OPEN'  1*     28.091      0.311   2468.439  2*         'Y'     17.244 /
     'WI_2'   33   55   12   12      'OPEN'  1*     21.884      0.311   1923.397  2*         'Y'     17.262 /
     'WI_2'   33   55   13   13      'OPEN'  1*     17.321      0.311   1522.701  2*         'Y'     17.280 /
-------------------------------------------------------------------------------------------------------------  
     'WI_3'   18   58    1    1      'OPEN'  1*      6.546      0.311    589.871  2*         'Y'     19.446 /
     'WI_3'   18   58    2    2      'OPEN'  1*     19.103      0.311   1721.809  2*         'Y'     19.464 /
     'WI_3'   18   58    3    3      'OPEN'  1*     40.975      0.311   3693.960  2*         'Y'     19.483 /
     'WI_3'   18   58    4    4      'OPEN'  1*     55.003      0.311   4959.543  2*         'Y'     19.501 /
     'WI_3'   18   58    5    5      'OPEN'  1*     56.811      0.311   5123.636  2*         'Y'     19.521 /
     'WI_3'   18   58    6    6      'OPEN'  1*     43.942      0.311   3963.731  2*         'Y'     19.539 /
     'WI_3'   18   58    7    7      'OPEN'  1*     40.040      0.311   3612.526  2*         'Y'     19.559 /
     'WI_3'   18   58    8    8      'OPEN'  1*     33.836      0.311   3053.396  2*         'Y'     19.578 /
     'WI_3'   18   58    9    9      'OPEN'  1*     32.345      0.311   2919.427  2*         'Y'     19.597 /
     'WI_3'   18   58   10   10      'OPEN'  1*     28.510      0.311   2573.795  2*         'Y'     19.616 /
     'WI_3'   18   58   11   11      'OPEN'  1*     30.111      0.311   2718.973  2*         'Y'     19.636 /
     'WI_3'   18   58   12   12      'OPEN'  1*      5.955      0.311    537.842  2*         'Y'     19.657 /
/

--set up lists of wel names


-- controls on automatic drilling of new wells

---Drilling time of each well. update this part
WDRILTIM
% for elem in drillingtime:
${"  {} {} YES /".format(elem[0],elem[1])}
% endfor
/ 


--outputs current RPT for the wells at this time and all subsequent report times.
WRFTPLT
'*' YES /
/

-- PRODUCTION WELL CONTROLS

WCONPROD
'OP_*'  AUTO  BHP   6000.00 4*  250  /
/

WCONINJE
'WI_*'  WATER AUTO RATE  10000.0   1* 320  1*  1*    1*   /
/

DATES

% for i in range(len(days)):
<% 
c_date = startdate + dt.timedelta(days=days[i])
tot_month = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JLY', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
%>
${"{0} {1} {2} /".format(c_date.day, tot_month[c_date.month-1],c_date.year)}
% endfor
/



END
