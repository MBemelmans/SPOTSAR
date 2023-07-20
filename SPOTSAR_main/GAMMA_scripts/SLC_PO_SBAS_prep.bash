!/bin/bash

###############################################################################
######### Bulk-processing of multi-kernel Sub-Pixel Offset Tracking ###########
###############################################################################
## this script takes an input text file with the parameters and pair names   ##
## for pixel offset trackign using multiple window sizes (kernels)           ##
## Created: Mark Bemelmans 11/08/2022, Bristol                               ##
## After gamma_mli_coreg_with_dem                                            ##
###############################################################################

##### input check functions #####
check_pos_int () {
    if [[ ! "$1" =~ ^[1-9][0-9]*$ ]];
    then
        echo "$1 is NOT a POSITIVE integer"
        exit -1
    fi
}

check_pos_float () {
    if [[ ! "$1" =~ ^[0-9]*.?[0-9]+$ ]];
    then
        echo "$1 is NOT a POSITIVE FLOAT"
        exit -1
    fi
}

check_pos_float_int () {
    if ! [[ $1 =~ ^[0-9]+$ ]] && ! [[ $1 =~ ^[0-9]*\.[0-9]+$ ]];
    then
        echo "$1 is NOT a POSITIVE FLOAT or POSITIVE INT"
        exit -1
    fi
}

check_int () {
    if [[ ! "$1" =~ ^-?[1-9][0-9]*$ ]];
    then
        echo "$1 is NOT an integer"
        exit -1
    fi
}

#### execute command function #####
## This function is pre-pended   ##
## any GAMMA function and will   ##
## run the command + log the     ##
## output in the $LOG file       ##
## if 'show' is part of the      ##
## command, the output will also ##
## be shown on screen            ##
###################################
function exec_cmd() {
    showintty=false
    numargs=$#
    prog2run=$1
    prog_str="$prog2run "
    shift # this removes $1 from the argument list causing $# to be decremented by 1 and making $2 the new $1
    while [ $# -gt 0 ]; do
        if [ "$1" == "show" ]; then
            showintty=true
        else
            prog_str+="$1 "
        fi
        shift
    done
    echo "Executing the command: ${prog_str}, $showintty"
    if $showintty; then
        eval $prog_str | tee -a $LOG
    else
        eval $prog_str >> $LOG
    fi
    echo " "
}

## DOC string ##
if [ "$#" == "0" ]; then
  echo " "
  echo " usage: SLC_PO_SBAS_prep.bash PROC_FILE START_PAIR END_PAIR"
  echo " e.g. SLC_PO_SBAS_prep.bash ./csk_dsc_PO_SBAS.param 1 10"
  echo " Processes SLC data for coregistration using external DEM "
  echo " performs sub-pixel offset tracking on SLC DATA using offset_pwr_tracking2"
  echo " calculates offsets using multiple window sizes using the previous larger window as a guide for the next."
  echo " created: Mark Bemelmans 11/08/2022, Bristol"
  echo " after gamma_mli_coreg_with_dem"
  exit
fi

## input control ##
if [ $# != 3 ]; then
  echo "Not right number of input arguments. Should be 3."
  echo "Type 'SLC_PO_SBAS_prep.bash' for help."
  exit -1
fi

## check par file ##
paramfile=$1
if [ -f $paramfile ]; then
        echo "Using parameter file $paramfile"
else
        echo "\033[1;31m ERROR - Parameter file $paramfile missing - Exiting \033[0m"
        exit -1
fi

## parse start and end pair ##
START_PAIR=$2
END_PAIR=$3

## read in parameters ##
source read_PO_params_2.sh

## set script name for logging ##
script_name='(SLC_PO_SBAS_prep)'

## calculate pixel offset step size scaled by multi-looking factors, if desired ##
if [ $step_win_flag == 0 ]; then
  let map_rlks=rstep*RLKS
  let map_alks=azstep*ALKS
fi

## set log ##
LOG=SLC_PO_SBAS_prep.log
rm -f $LOG
date | tee $LOG


## user input to ask for pre-processing ##
## Pre-processing involves creating the ##
## common reference RSLC and the .lat   ##
## and .lon files whic are then stored  ##
## in ./geo.                            ##
echo "Do you wish to do pre-processing? (y/n): "
read ANSWER

if [ $ANSWER == "y" ]; then
  source geocode_ref_slc_2.sh
fi 

## reset script name ##
script_name='(SLC_PO_SBAS_prep)'

## collect number of lines and samples from cropping values ##
if [ $cropping_flag == 1 ]; then
  let n_samples_crop=rstop-rstart+1
  let n_lines_crop=astop-astart+1
fi

## make symlink to reference RSLC ##
echo " "
  ln -s ./RSLC/$COMMON_ref.rslc ./$COMMON_ref.rslc | tee -a $LOG
echo " "

## perform cropping on reference SLC ##
if [ $cropping_flag == 1 ]; then
  # crop .rslcs with SLC_copy to extract smaller area around the volcano
  exec_cmd SLC_copy $COMMON_ref.rslc $COMMON_ref.rslc.par $COMMON_ref.crop.rslc $COMMON_ref.crop.rslc.par 4 - $rstart $n_samples_crop $astart $n_lines_crop - - show
fi

## create DEM files that fit step-size of Pixel offset tracking ##
exec_cmd create_PO_DEM_files $cropping_flag $COMMON_ref $DEM $DEM_PAR $map_rlks $map_alks $demlat $demlon show

## reset script name ##
script_name='(SLC_PO_SBAS_prep)'

## for all pairs repeat steps 5-x ##
x=$START_PAIR

while [ $x -le $END_PAIR ];
do
  echo "making pair $x"
  if [ $x -lt 10 ]; then
        ORBIT1=ref_ORBIT00$x
        ORBIT2=int_ORBIT00$x
  fi
  if [[ $x -gt 9 && $x -lt 100 ]]; then
        echo "x>=10 is satisfied"
        ORBIT1=ref_ORBIT0$x
        ORBIT2=int_ORBIT0$x
  fi
  if [[ $x -gt 99 && $x -lt 1000 ]]; then
        ORBIT1=ref_ORBIT$x
        ORBIT2=int_ORBIT$x
  fi
  echo "$ORBIT1 $ORBIT2"
  # echo "awk '$1 == `$ORBIT_ref` {print $2}' $proc_file"
  ORBIT_ref=`grep $ORBIT1 $paramfile | awk '{print $2}'`
  ORBIT_sec=`grep $ORBIT2 $paramfile | awk '{print $2}'`
  # pwd
  if [ ! -d "./$ORBIT_ref" ]; then
  # if SLC folder is not present, make SLC of acquisitions in pair x
    if [ $sat_tag == "CSK" ]; then
      exec_cmd CSK_MAKE_SLC $DATA_dir $COMMON_ref 1 $RLKS $ALKS show
    fi
  
    if [ $sat_tag == "TSX" ]; then
      exec_cmd CSK_MAKE_TSX $DATA_dir $COMMON_ref 1 $RLKS $ALKS show
    fi
  fi
  if [ ! -d "./$ORBIT_sec" ]; then
  # if SLC folder is not present, make SLC of acquisitions in pair x
    if [ $sat_tag == "CSK" ]; then
      exec_cmd CSK_MAKE_SLC $DATA_dir $COMMON_sec 1 $RLKS $ALKS show
    fi
  
    if [ $sat_tag == "TSX" ]; then
      exec_cmd CSK_MAKE_TSX $DATA_dir $COMMON_sec 1 $RLKS $ALKS show
    fi
  fi


  source run_PO_on_pair_2.sh

  echo "completed pair $x, on to the next one!"
  cd ../..
  # pwd
  x=$(($x + 1))
done

echo "PO_SBAS prep completed!