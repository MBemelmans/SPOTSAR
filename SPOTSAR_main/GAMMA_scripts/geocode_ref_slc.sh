### this is a section of bash script to be inserted into SLC_PO_SBAS_prep.bash using source
### geocode_ref_slc.sh performs geocoding on stack reference SLC to get .lat/.lon files
### created July 2023, Mark Bemelmans, Bristol

  script_name = '(geocode_ref_slc)'
  echo "$script_name step 2: Make folders and SLCs"
  
  # TO-DO:
  # - make SLC based on satellite tag (e.g., CSK, TSK)
  if [ $sat_tag == "CSK" ]; then
    exec_cmd CSK_MAKE_SLC $DATA_dir $COMMON_ref 1 $RLKS $ALKS show
  fi

  if [ $sat_tag == "TSX" ]; then
    exec_cmd CSK_MAKE_TSX $DATA_dir $COMMON_ref 1 $RLKS $ALKS show
  fi
  cd ./$COMMON_ref
  pwd
  #echo "multi_look $COMMON_ref.slc $COMMON_ref.slc.par ${COMMON_ref}_${map_rlks}_${map_alks}.mli ${COMMON_ref}_${map_rlks}_${map_alks}.mli.par $RLKS $ALKS"
  exec_cmd multi_look $COMMON_ref.slc $COMMON_ref.slc.par ${COMMON_ref}_${map_rlks}_${map_alks}.mli ${COMMON_ref}_${map_rlks}_${map_alks}.mli.par $RLKS $ALKS show
  ls -l
  cd ../RSLC
  if [ ! -f $COMMON_ref.rslc.par ]; then
      ln -s ../$COMMON_ref/$COMMON_ref.slc.par ./$COMMON_ref.rslc.par
      echo " "
  fi
  if [ ! -f $COMMON_ref.rslc ]; then
      ln -s ../$COMMON_ref/$COMMON_ref.slc ./$COMMON_ref.rslc
      echo " "
  fi
  if [ ! -f $COMMON_ref.rmli.par ]; then
      ln -s ../$COMMON_ref/$COMMON_ref.mli.par ./$COMMON_ref.rmli.par
      echo " "
  fi
  if [ ! -f $COMMON_ref.rmli ]; then
      ln -s ../$COMMON_ref/$COMMON_ref.mli ./$COMMON_ref.rmli
      echo " "
  fi
  echo "ls for RSLC"
  ls -l

  cd ..
  echo "$script_name step 3: convert DEM into COMMON_ref radar coordinates and move into ./geo folder"
  if [ -f $COMMON_ref.rslc.par ]; then
    rm -rf $COMMON_ref.rslc.par
  fi
  echo " "
  if [ ! -f $COMMON_ref.rslc.par ]; then
      ln -s ./RSLC/$COMMON_ref.rslc.par .
      echo " "
  fi

  if [ -f ${COMMON_ref}.rmli.par ]; then
    rm -rf ${COMMON_ref}.rmli.par
  fi
  echo " "
  if [ ! -f ${COMMON_ref}.rmli.par ]; then
      ln -s ./RSLC/${COMMON_ref}.rmli.par . #BME - Why is there no target specified (like ".")"?
      echo " "
  fi

  # #echo "gc_map2 $COMMON_ref.rslc.par $DEM_PAR $DEM $COMMON_ref.dem_seg.par $COMMON_ref.dem_seg $COMMON_ref.map_to_rdc $demlat $demlon - -"
  # exec_cmd gc_map2 $COMMON_ref.rslc.par $DEM_PAR $DEM $COMMON_ref.dem_seg.par $COMMON_ref.dem_seg $COMMON_ref.map_to_rdc $demlat $demlon - - show

  ###   Transformation of DEM to SAR coordinates:  $HGT_SIM:
  DATE0=`echo ${COMMON_ref} | tr -cd '[[:digit:]]'`

  #echo "gc_map2 ${COMMON_ref}.rslc.par $DEM_PAR $DEM ${COMMON_ref}.dem_seg.par ${COMMON_ref}.dem_seg ${COMMON_ref}.map_to_rdc $demlat $demlon - -"
  exec_cmd gc_map2 ${COMMON_ref}.rslc.par $DEM_PAR $DEM ${COMMON_ref}.dem_seg.par ${COMMON_ref}.dem_seg ${COMMON_ref}.map_to_rdc $demlat $demlon - - show

  map_width=`awk '$1 == "width:" {print $2}' ${COMMON_ref}.dem_seg.par`
  width=`awk '$1 == "range_samples:" {print $2}' ${COMMON_ref}.rslc.par`
  lines=`awk '$1 == "azimuth_lines:" {print $2}' ${COMMON_ref}.rslc.par`
  echo "map segment width: $map_width       SAR data width, lines: $width $lines"
  echo ""
  echo "Transformation of DEM into SAR coordinates:  ${COMMON_ref}.dem.rdc"
  #echo "geocode ${COMMON_ref}.map_to_rdc ${COMMON_ref}.dem_seg $map_width ${DATE0}.dem.rdc $width $lines 0 0"
  exec_cmd geocode ${COMMON_ref}.map_to_rdc ${COMMON_ref}.dem_seg $map_width ${DATE0}.dem.rdc $width $lines 0 0 show

  echo "$script_name step 3b: create .lat and .lon files for pixel offset"
  #echo "dem_coord ${COMMON_ref}.dem_seg.par ${DATE0}.real.lon ${DATE0}.real.lat | tee -a $LOG"
  exec_cmd dem_coord ${COMMON_ref}.dem_seg.par ${DATE0}.real.lon ${DATE0}.real.lat show
  #echo "geocode ${COMMON_ref}.map_to_rdc ${DATE0}.real.lon $map_width ${DATE0}.lon $width $lines 0 0 | tee -a $LOG"
  exec_cmd geocode ${COMMON_ref}.map_to_rdc ${DATE0}.real.lon $map_width ${DATE0}.lon $width $lines 0 0 show
  #echo "geocode ${COMMON_ref}.map_to_rdc ${DATE0}.real.lat $map_width ${DATE0}.lat $width $lines 0 0 | tee -a $LOG"
  exec_cmd geocode ${COMMON_ref}.map_to_rdc ${DATE0}.real.lat $map_width ${DATE0}.lat $width $lines 0 0 show
  # these files need to beconverted to .lat and .lon using matlab convertGAMMAEastNorth2latlon
  rm -rf ${DATE0}.real.*


  if [ -d "./geo" ]; then
    rm -rf ./geo
  fi

  if [ ! -d "./geo" ]; then
    mkdir ./geo
  fi

  mv $DATE0.dem.rdc ./geo/
  mv $DATE0.lon ./geo/
  mv $DATE0.lat ./geo/