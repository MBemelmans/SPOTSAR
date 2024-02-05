### this is a section of bash script to be inserted into SLC_PO_SBAS_prep.bash using source
### read_PO_params.sh loads the parameters into memory
### created July 2023, Mark Bemelmans, Bristol


paramfile = $1
script_name = '(read_PO_params)'
# read parameter file
echo "$script_name step 1: read parameter file"

DATA_dir=`grep data_dir $paramfile | awk '{print $2}'`
if [ ! -d $DATA_dir ]; then
  echo "ERROR: DATA_dir is not a directory"
  echo "current DATA_dir: $DATA_dir"
  exit -1
fi

sat_tag=`grep sat_tag $paramfile | awk '{print $2}'`
COMMON_ref=`grep COMMON_ref $paramfile | awk '{print $2}'`

# DEM params
DEM=`grep dem_file $paramfile | awk '{print $2}'`
if [ ! -f $DEM ]; then
  echo "ERROR: DEM file does not excists"
  echo "current DEM: $DEM"
  exit -1
fi
DEM_PAR=`grep dem_par $paramfile | awk '{print $2}'`
if [ ! -f $DEM_PAR ]; then
  echo "ERROR: DEM_PAR file does not excists"
  echo "current DEM_PAR: $DEM_PAR"
  exit -1
fi
# DEM sampling params
demlat=`grep demlat $paramfile | awk '{print $2}'` # DEM oversampling factor in latitude used for coregistration
demlon=`grep demlon $paramfile | awk '{print $2}'` # DEM oversampling factor in longitude used for coregistration
gclat=`grep gc_lat $paramfile | awk '{print $2}'`  # DEM oversampling factor in latitude used for geodocing PO results
gclon=`grep gc_lon $paramfile | awk '{print $2}'`  # DEM oversampling factor in longitude used for geodocing PO results

check_pos_float_int $demlat
check_pos_float_int $demlon
check_pos_float_int $gclat
check_pos_float_int $gclon

# Number of Looks
# MLI params
RLKS=`grep RLKS $paramfile | awk '{print $2}'`
ALKS=`grep ALKS $paramfile | awk '{print $2}'`

check_pos_int $RLKS
check_pos_int $ALKS

# RSLC cropping parameters
rstart=`grep rstart $paramfile | awk '{print $2}'`
rstop=`grep rstop $paramfile | awk '{print $2}'`
astart=`grep astart $paramfile | awk '{print $2}'`
astop=`grep astop $paramfile | awk '{print $2}'`

check_pos_int $rstart
check_pos_int $rstop
check_pos_int $astart
check_pos_int $astop

cropping_flag=`grep cropping_flag $paramfile | awk '{print $2}'`;  # step and window size flag 0 for calculate from rwin/rstep/RLKS; 1 for set explicitely
if [[ $cropping_flag -ne 0 && $cropping_flag -ne 1 ]]; then
    echo "cropping_flag should be either 0 or 1"
    exit -1
fi

step_win_flag=`grep step_win_flag $paramfile | awk '{print $2}'`;  # step and window size flag 0 for calculate from rwin/rstep/RLKS; 1 for set explicitely
if [[ $step_win_flag -ne 0 && $step_win_flag -ne 1 ]]; then
    echo "step_win_flag should be either 0 or 1"
    exit -1
fi
#offset tracking params (to use in calculation with RLKS/ALKS)
rwin=`grep rwin $paramfile | awk '{print $2}'`  # Window size in Range
azwin=`grep azwin $paramfile | awk '{print $2}'` # Window size in Azimuth
rstep=`grep rstep $paramfile | awk '{print $2}'` # Step size in Range
azstep=`grep azstep $paramfile | awk '{print $2}'` # Step size in Azimuth

check_pos_int $rwin
check_pos_int $azwin
check_pos_int $rstep
check_pos_int $azstep

#offset tracking params (to use SEPERATE FROM RLKS/ALKS)
map_rlks=`grep map_rlks $paramfile | awk '{print $2}'`
map_alks=`grep map_alks $paramfile | awk '{print $2}'`
slc_rwin=`grep rngwin_PO $paramfile | awk '{print $2}'`
slc_azwin=`grep aziwin_PO $paramfile | awk '{print $2}'`

check_pos_int $map_rlks
check_pos_int $map_alks
check_pos_int $slc_rwin
check_pos_int $slc_azwin

ccpthresh=`grep ccpthresh $paramfile | awk '{print $2}'` # the cross-correlation threshold to accept offset value
bwfrac=`grep bwfrac $paramfile | awk '{print $2}'` # bandwidth fraction for window matching in offset_pwr_trackingm
SLC_ovr=`grep SLC_ovr $paramfile | awk '{print $2}'` # SLC oversampling factor, generally 2 is recommended
final_cpthresh=`grep final_ccpthresh $paramfile | awk '{print $2}'` # cross-correlation threshold to accept offset estimates from offset_pwr_trackingm

check_pos_float $ccpthresh
check_pos_float $bwfrac
check_pos_int $SLC_ovr
check_pos_float $final_cpthresh