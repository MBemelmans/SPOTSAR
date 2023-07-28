#!/bin/bash


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





if [ "$#" == "0" ]; then
  echo " "
  echo " usage: create_PO_DEM_files cropping_flag COMMON_ref DEM DEM_PAR map_rlks map_alks demlat demlon LOG"
  echo " Processes reference SLC data and DEM to make .lon and .lat files "
  echo " created: Mark Bemelmans July 2023, Bristol"
  exit
fi

# input control
if [ $# != 9 ]; then
  echo "Not right number of input arguments. Should be 9."
  echo "Type 'create_PO_DEM_files' for help."
  exit -1
fi

script_name='(create_latlon_files)'
cropping_flag=$1
COMMON_ref=$2
DEM=$3
DEM_PAR=$4
map_rlks=$5
map_alks=$6
demlat=$7
demlon=$8
LOG=$9

if [ $cropping_flag == 1 ]; then

  exec_cmd multi_look $COMMON_ref.crop.rslc $COMMON_ref.crop.rslc.par ${COMMON_ref}_${map_rlks}_${map_alks}.crop.rmli ${COMMON_ref}_${map_rlks}_${map_alks}.crop.rmli.par $map_rlks $map_alks show
  width_mli=`awk '$1 == "range_samples:" {print $2}' ${COMMON_ref}_${map_rlks}_${map_alks}.crop.rmli.par`
  
  echo "$script_name step 6: geocode for the PO products"
  #echo "gc_map2 ${ORBIT_ref}_${map_rlks}_${map_alks}.rmli.par $DEM_PAR $DEM ${ORBIT_ref}_${map_rlks}_${map_alks}.dem_seg.par ${ORBIT_ref}_${map_rlks}_${map_alks}.dem_seg ${ORBIT_ref}_${map_rlks}_${map_alks}.map_to_rdc $demlat $demlon - -" >>$LOG
  exec_cmd gc_map2 ${COMMON_ref}_${map_rlks}_${map_alks}.crop.rmli.par $DEM_PAR $DEM ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg ${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc $demlat $demlon - - show
  
  
  ###   Transformation of DEM to SAR coordinates:  $HGT_SIM:
  
  echo ""
  map_width=`awk '$1 == "width:" {print $2}' ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par`
  width=`awk '$1 == "range_samples:" {print $2}' ${COMMON_ref}_${map_rlks}_${map_alks}.crop.rmli.par`
  echo "map segment width: $map_width       SAR data width: $width"
  echo ""
  echo "Transformation of DEM into SAR coordinates:  ${COMMON_ref}_${map_rlks}_${map_alks}.dem.rdc"
  echo "parse (cropped) SLC width to file SLC_width.txt"
  echo "$width" > SLC_width.txt
fi

if [ $cropping_flag == 0 ]; then
  exec_cmd multi_look $COMMON_ref.rslc $COMMON_ref.rslc.par ${COMMON_ref}_${map_rlks}_${map_alks}.rmli ${COMMON_ref}_${map_rlks}_${map_alks}.rmli.par $map_rlks $map_alks show
  width_mli=`awk '$1 == "range_samples:" {print $2}' ${COMMON_ref}_${map_rlks}_${map_alks}.rmli.par`
  
  echo "$script_name step 6: geocode for the PO products"
  #echo "gc_map2 ${ORBIT_ref}_${map_rlks}_${map_alks}.rmli.par $DEM_PAR $DEM ${ORBIT_ref}_${map_rlks}_${map_alks}.dem_seg.par ${ORBIT_ref}_${map_rlks}_${map_alks}.dem_seg ${ORBIT_ref}_${map_rlks}_${map_alks}.map_to_rdc $demlat $demlon - -" >>$LOG
  exec_cmd gc_map2 ${COMMON_ref}_${map_rlks}_${map_alks}.rmli.par $DEM_PAR $DEM ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg ${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc $demlat $demlon - - show
  
  ###   Transformation of DEM to SAR coordinates:  $HGT_SIM:
  
  echo ""
  map_width=`awk '$1 == "width:" {print $2}' ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par`
  width=`awk '$1 == "range_samples:" {print $2}' ${COMMON_ref}_${map_rlks}_${map_alks}.rmli.par`
  echo "map segment width: $map_width       SAR data width: $width"
  echo ""
  echo "Transformation of DEM into SAR coordinates:  ${COMMON_ref}_${map_rlks}_${map_alks}.dem.rdc"
  echo "parse (cropped) SLC width to file SLC_width.txt"
  $width > SLC_width.txt
fi


#echo "geocode ${ORBIT_ref}_${map_rlks}_${map_alks}.map_to_rdc ${ORBIT_ref}_${map_rlks}_${map_alks}.dem_seg $map_width ${ORBIT_ref}_${map_rlks}_${map_alks}.dem.rdc $width 0 0 0"
exec_cmd geocode ${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg $map_width ${COMMON_ref}_${map_rlks}_${map_alks}.dem.rdc $width 0 0 0 show

if [ -d PO_geocoding ]; then
    rm -rf PO_geocoding
fi
mkdir PO_geocoding
mv ${COMMON_ref}_${map_rlks}_${map_alks}.* ./PO_geocoding/