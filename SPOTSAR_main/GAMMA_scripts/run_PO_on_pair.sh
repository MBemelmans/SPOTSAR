### this is a section of bash script to be inserted into SLC_PO_SBAS_prep.bash using source
### run_PO_on_pair.sh performs pixel offset tracking on an image pair using offset_pwr_tracking2
### created July 2023, Mark Bemelmans, Bristol

  echo "$script_name step 4: coregister SLC with DEM (only if RSLC does not excist yet)"
  echo "rwin: $rwin azwin: $azwin slc_rwin: $slc_rwin slc_azwin: $slc_azwin"

  echo "generate pair $ORBIT_ref $ORBIT_sec"
  if [ ! -f "./RSLC/${ORBIT_ref}.rslc" ]; then
    #echo "slc_coreg_with_dem_v3 $COMMON_ref $ORBIT_ref $DEM $DEM_PAR"
    exec_cmd slc_coreg_with_dem_v3 $COMMON_ref $ORBIT_ref $DEM $DEM_PAR $demlat $demlon $RLKS $ALKS show
  fi

  if [ ! -f "./RSLC/${ORBIT_sec}.rslc" ]; then
    #echo "slc_coreg_with_dem_v3 $COMMON_ref $ORBIT_sec $DEM $DEM_PAR"
    exec_cmd slc_coreg_with_dem_v3 $COMMON_ref $ORBIT_sec $DEM $DEM_PAR $demlat $demlon $RLKS $ALKS show
  fi

  # MAKE NEW IMAGE PAIR FOLDER
  PAIRNAME=${ORBIT_ref}_${ORBIT_sec}
  cd ./PO_SBAS_PAIRS/

  if [ -d "$PAIRNAME" ]; then
    rm -rf $PAIRNAME
  fi

  if [ ! -d "$PAIRNAME" ]; then
    mkdir $PAIRNAME
  fi
  cd $PAIRNAME

  # MAKE LINKS TO REQUIRED FILES
  ln -s ../../RSLC/$ORBIT_ref.rslc ./$ORBIT_ref.rslc | tee -a $LOG
  ln -s ../../RSLC/$ORBIT_ref.rslc.par ./$ORBIT_ref.rslc.par | tee -a $LOG
  ln -s ../../RSLC/$ORBIT_sec.rslc ./$ORBIT_sec.rslc | tee -a $LOG
  ln -s ../../RSLC/$ORBIT_sec.rslc.par ./$ORBIT_sec.rslc.par | tee -a $LOG
  ln -s ../../RSLC/$COMMON_ref.rslc ./$COMMON_ref.rslc | tee -a $LOG
  ln -s ../../RSLC/$COMMON_ref.rslc.par ./$COMMON_ref.rslc.par | tee -a $LOG
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.rmli ./${COMMON_ref}_${map_rlks}_${map_alks}.rmli | tee -a $LOG
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.rmli.par ./${COMMON_ref}_${map_rlks}_${map_alks}.rmli.par | tee -a $LOG
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc ./${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc | tee -a $LOG
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg ./${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg | tee -a $LOG
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ./${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par | tee -a $LOG

  if [ $cropping_flag == 1 ]; then
    # crop RSLCs
    # SLC_copy <SLC_in> <SLC_par_in> <SLC_out> <SLC_par_out> [fcase] [sc] [roff] [nr] [loff] [nl] [swap_IQ] [header_lines]
    exec_cmd SLC_copy $COMMON_ref.rslc $COMMON_ref.rslc.par $COMMON_ref.crop.rslc $COMMON_ref.crop.rslc.par 4 - $rstart $n_samples_crop $astart $n_lines_crop - - show
    exec_cmd SLC_copy $ORBIT_ref.rslc $ORBIT_ref.rslc.par $ORBIT_ref.crop.rslc $ORBIT_ref.crop.rslc.par 4 - $rstart $n_samples_crop $astart $n_lines_crop - - show
    exec_cmd SLC_copy $ORBIT_sec.rslc $ORBIT_sec.rslc.par $ORBIT_sec.crop.rslc $ORBIT_sec.crop.rslc.par 4 - $rstart $n_samples_crop $astart $n_lines_crop - - show
  
    # create initial offset par file
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par $PAIRNAME_${init_rwin}_${init_awin}.off_par_init 1 1 1 0 show
  
    echo "$script_name step 5: offset tracking with initial large window size (e.g., 256-by-256)"
    exec_cmd offset_pwr $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par $PAIRNAME.off_par_init offs_${init_rwin}_${init_awin} ccp_${init_rwin}_${init_awin} $init_rwin $init_awin offsets_${init_rwin}_${init_awin}.txt - - - $ccpthresh 9 - - - show
    exec_cmd offset_fit offs_${init_rwin}_${init_awin} ccp_${init_rwin}_${init_awin} $PAIRNAME_${init_rwin}_${init_awin}.off_par_init coffs_${init_rwin}_${init_awin} coffsets_${init_rwin}_${init_awin}.txt $ccpthresh 4 0 show
    
  
    # create off_par for windwo sizes going down
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par $PAIRNAME_${rwin1}_${awin1}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par $PAIRNAME_${rwin2}_${awin2}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par $PAIRNAME_${rwin3}_${awin3}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par $PAIRNAME_${rwin4}_${awin4}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par $PAIRNAME_${rwin5}_${awin5}.off_par 1 1 1 0 show
  
  
    # calculate window size dependent on multi-looking values
    if [ $step_win_flag == 0 ]; then
        let slc_rwin1=rwin1*RLKS
        let slc_azwin1=azwin1*ALKS

        let slc_rwin2=rwin2*RLKS
        let slc_azwin2=azwin2*ALKS

        let slc_rwin3=rwin3*RLKS
        let slc_azwin3=azwin3*ALKS

        let slc_rwin4=rwin4*RLKS
        let slc_azwin4=azwin4*ALKS

        let slc_rwin5=rwin5*RLKS
        let slc_azwin5=azwin5*ALKS
    fi

    # make multiple window size pixel offsets
    # rwin1
    echo "rwin: $rwin1 azwin: $azwin1 slc_rwin: $slc_rwin1 slc_azwin: $slc_azwin1"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  $PAIRNAME_${rwin1}_${awin1}.off_par offs_${rwin1}_${awin1} ccp_${rwin1}_${awin1} \
                                  $PAIRNAME_${init_rwin}_${init_awin}.off_par_init offs_${init_rwin}_${init_awin} \
                                  $slc_rwin $slc_azwin offsets_${rwin1}_${awin1}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin1}_${awin1} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin1}_${awin1} ccp_${rwin1}_${awin1} ${PAIRNAME}_${rwin1}_${awin1}.off_par coffs_${rwin1}_${awin1} coffsets_${rwin1}_${awin1}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin1}_${awin1} ccp_${rwin1}_${awin1} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin1}_${awin1}.off_par disp_${rwin1}_${awin1}_coffs disp_${rwin1}_${awin1}.txt 1 $final_cpthresh 1 show

    #rwin2
    echo "rwin: $rwin2 azwin: $azwin2 slc_rwin: $slc_rwin2 slc_azwin: $slc_azwin2"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  $PAIRNAME_${rwin2}_${awin2}.off_par offs_${rwin2}_${awin2} ccp_${rwin2}_${awin2} \
                                  $PAIRNAME_${rwin1}_${awin1}.off_par offs_${rwin1}_${awin1} \
                                  $slc_rwin $slc_azwin offsets_${rwin2}_${awin2}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin2}_${awin2} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin2}_${awin2} ccp_${rwin2}_${awin2} ${PAIRNAME}_${rwin2}_${awin2}.off_par coffs_${rwin2}_${awin2} coffsets_${rwin2}_${awin2}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin2}_${awin2} ccp_${rwin2}_${awin2} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin2}_${awin2}.off_par disp_${rwin2}_${awin2}_coffs disp_${rwin2}_${awin2}.txt 1 $final_cpthresh 1 show

    #rwin3
    echo "rwin: $rwin3 azwin: $azwin3 slc_rwin: $slc_rwin3 slc_azwin: $slc_azwin3"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  $PAIRNAME_${rwin3}_${awin3}.off_par offs_${rwin3}_${awin3} ccp_${rwin3}_${awin3} \
                                  $PAIRNAME_${rwin2}_${awin2}.off_par offs_${rwin2}_${awin2} \
                                  $slc_rwin $slc_azwin offsets_${rwin3}_${awin3}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin3}_${awin3} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin3}_${awin3} ccp_${rwin3}_${awin3} ${PAIRNAME}_${rwin3}_${awin3}.off_par coffs_${rwin3}_${awin3} coffsets_${rwin3}_${awin3}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin3}_${awin3} ccp_${rwin3}_${awin3} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin3}_${awin3}.off_par disp_${rwin3}_${awin3}_coffs disp_${rwin3}_${awin3}.txt 1 $final_cpthresh 1 show

    #rwin4
    echo "rwin: $rwin4 azwin: $azwin4 slc_rwin: $slc_rwin4 slc_azwin: $slc_azwin4"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  $PAIRNAME_${rwin4}_${awin4}.off_par offs_${rwin4}_${awin4} ccp_${rwin4}_${awin4} \
                                  $PAIRNAME_${rwin3}_${awin3}.off_par offs_${rwin3}_${awin3} \
                                  $slc_rwin $slc_azwin offsets_${rwin4}_${awin4}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin4}_${awin4} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin4}_${awin4} ccp_${rwin4}_${awin4} ${PAIRNAME}_${rwin4}_${awin4}.off_par coffs_${rwin4}_${awin4} coffsets_${rwin4}_${awin4}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin4}_${awin4} ccp_${rwin4}_${awin4} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin4}_${awin4}.off_par disp_${rwin4}_${awin4}_coffs disp_${rwin4}_${awin4}.txt 1 $final_cpthresh 1 show

    #rwin4
    echo "rwin: $rwin5 azwin: $azwin5 slc_rwin: $slc_rwin5 slc_azwin: $slc_azwin5"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  $PAIRNAME_${rwin5}_${awin5}.off_par offs_${rwin5}_${awin5} ccp_${rwin5}_${awin5} \
                                  $PAIRNAME_${rwin4}_${awin4}.off_par offs_${rwin4}_${awin4} \
                                  $slc_rwin $slc_azwin offsets_${rwin5}_${awin5}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin5}_${awin5} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin5}_${awin5} ccp_${rwin5}_${awin5} ${PAIRNAME}_${rwin5}_${awin5}.off_par coffs_${rwin5}_${awin5} coffsets_${rwin5}_${awin5}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin5}_${awin5} ccp_${rwin5}_${awin5} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin5}_${awin5}.off_par disp_${rwin5}_${awin5}_coffs disp_${rwin5}_${awin5}.txt 1 $final_cpthresh 1 show

  fi
  
  if [ $cropping_flag == 0 ]; then
    # create initial offset par file
    exec_cmd create_offset $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par $PAIRNAME_${init_rwin}_${init_awin}.off_par_init 1 1 1 0 show
  
    echo "$script_name step 5: offset tracking with initial large window size (e.g., 256-by-256)"
    exec_cmd offset_pwr $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par $PAIRNAME.off_par_init offs_${init_rwin}_${init_awin} ccp_${init_rwin}_${init_awin} $init_rwin $init_awin offsets_${init_rwin}_${init_awin}.txt - - - $ccpthresh 9 - - - show
    exec_cmd offset_fit offs_${init_rwin}_${init_awin} ccp_${init_rwin}_${init_awin} $PAIRNAME_${init_rwin}_${init_awin}.off_par_init coffs_${init_rwin}_${init_awin} coffsets_${init_rwin}_${init_awin}.txt $ccpthresh 4 0 show
    
  
    # create off_par for windwo sizes going down
    exec_cmd create_offset $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par $PAIRNAME_${rwin1}_${awin1}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par $PAIRNAME_${rwin2}_${awin2}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par $PAIRNAME_${rwin3}_${awin3}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par $PAIRNAME_${rwin4}_${awin4}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par $PAIRNAME_${rwin5}_${awin5}.off_par 1 1 1 0 show
  
  
    # calculate window size dependent on multi-looking values
    if [ $step_win_flag == 0 ]; then
        let slc_rwin1=rwin1*RLKS
        let slc_azwin1=azwin1*ALKS

        let slc_rwin2=rwin2*RLKS
        let slc_azwin2=azwin2*ALKS

        let slc_rwin3=rwin3*RLKS
        let slc_azwin3=azwin3*ALKS

        let slc_rwin4=rwin4*RLKS
        let slc_azwin4=azwin4*ALKS

        let slc_rwin5=rwin5*RLKS
        let slc_azwin5=azwin5*ALKS
    fi

    # make multiple window size pixel offsets
    # rwin1
    echo "rwin: $rwin1 azwin: $azwin1 slc_rwin: $slc_rwin1 slc_azwin: $slc_azwin1"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  $PAIRNAME_${rwin1}_${awin1}.off_par offs_${rwin1}_${awin1} ccp_${rwin1}_${awin1} \
                                  $PAIRNAME_${init_rwin}_${init_awin}.off_par_init offs_${init_rwin}_${init_awin} \
                                  $slc_rwin $slc_azwin offsets_${rwin1}_${awin1}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin1}_${awin1} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin1}_${awin1} ccp_${rwin1}_${awin1} ${PAIRNAME}_${rwin1}_${awin1}.off_par coffs_${rwin1}_${awin1} coffsets_${rwin1}_${awin1}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin1}_${awin1} ccp_${rwin1}_${awin1} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin1}_${awin1}.off_par disp_${rwin1}_${awin1}_coffs disp_${rwin1}_${awin1}.txt 1 $final_cpthresh 1 show

    #rwin2
    echo "rwin: $rwin2 azwin: $azwin2 slc_rwin: $slc_rwin2 slc_azwin: $slc_azwin2"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  $PAIRNAME_${rwin2}_${awin2}.off_par offs_${rwin2}_${awin2} ccp_${rwin2}_${awin2} \
                                  $PAIRNAME_${rwin1}_${awin1}.off_par offs_${rwin1}_${awin1} \
                                  $slc_rwin $slc_azwin offsets_${rwin2}_${awin2}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin2}_${awin2} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin2}_${awin2} ccp_${rwin2}_${awin2} ${PAIRNAME}_${rwin2}_${awin2}.off_par coffs_${rwin2}_${awin2} coffsets_${rwin2}_${awin2}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin2}_${awin2} ccp_${rwin2}_${awin2} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin2}_${awin2}.off_par disp_${rwin2}_${awin2}_coffs disp_${rwin2}_${awin2}.txt 1 $final_cpthresh 1 show

    #rwin3
    echo "rwin: $rwin3 azwin: $azwin3 slc_rwin: $slc_rwin3 slc_azwin: $slc_azwin3"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  $PAIRNAME_${rwin3}_${awin3}.off_par offs_${rwin3}_${awin3} ccp_${rwin3}_${awin3} \
                                  $PAIRNAME_${rwin2}_${awin2}.off_par offs_${rwin2}_${awin2} \
                                  $slc_rwin $slc_azwin offsets_${rwin3}_${awin3}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin3}_${awin3} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin3}_${awin3} ccp_${rwin3}_${awin3} ${PAIRNAME}_${rwin3}_${awin3}.off_par coffs_${rwin3}_${awin3} coffsets_${rwin3}_${awin3}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin3}_${awin3} ccp_${rwin3}_${awin3} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin3}_${awin3}.off_par disp_${rwin3}_${awin3}_coffs disp_${rwin3}_${awin3}.txt 1 $final_cpthresh 1 show

    #rwin4
    echo "rwin: $rwin4 azwin: $azwin4 slc_rwin: $slc_rwin4 slc_azwin: $slc_azwin4"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  $PAIRNAME_${rwin4}_${awin4}.off_par offs_${rwin4}_${awin4} ccp_${rwin4}_${awin4} \
                                  $PAIRNAME_${rwin3}_${awin3}.off_par offs_${rwin3}_${awin3} \
                                  $slc_rwin $slc_azwin offsets_${rwin4}_${awin4}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin4}_${awin4} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin4}_${awin4} ccp_${rwin4}_${awin4} ${PAIRNAME}_${rwin4}_${awin4}.off_par coffs_${rwin4}_${awin4} coffsets_${rwin4}_${awin4}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin4}_${awin4} ccp_${rwin4}_${awin4} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin4}_${awin4}.off_par disp_${rwin4}_${awin4}_coffs disp_${rwin4}_${awin4}.txt 1 $final_cpthresh 1 show

    #rwin4
    echo "rwin: $rwin5 azwin: $azwin5 slc_rwin: $slc_rwin5 slc_azwin: $slc_azwin5"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  $PAIRNAME_${rwin5}_${awin5}.off_par offs_${rwin5}_${awin5} ccp_${rwin5}_${awin5} \
                                  $PAIRNAME_${rwin4}_${awin4}.off_par offs_${rwin4}_${awin4} \
                                  $slc_rwin $slc_azwin offsets_${rwin5}_${awin5}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${rwin5}_${awin5} show
  
    # offset_fit      <offs>    <ccp>     <OFF_par>          [coffs]    [coffsets]       [thres] [npoly] [interact_flag]
    exec_cmd offset_fit offs_${rwin5}_${awin5} ccp_${rwin5}_${awin5} ${PAIRNAME}_${rwin5}_${awin5}.off_par coffs_${rwin5}_${awin5} coffsets_${rwin5}_${awin5}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${rwin5}_${awin5} ccp_${rwin5}_${awin5} ${ORBIT_ref}.rslc.par $PAIRNAME_${rwin5}_${awin5}.off_par disp_${rwin5}_${awin5}_coffs disp_${rwin5}_${awin5}.txt 1 $final_cpthresh 1 show
  fi
  
  # get width of offset maps
  widthoff1=`grep range_samples $PAIRNAME_${rwin1}_${awin1}.off_par | awk '{print $2}'`
  echo '$widthoff1' > $PAIRNAME_${rwin1}_${awin1}_widthoff.txt
  widthoff2=`grep range_samples $PAIRNAME_${rwin2}_${awin2}.off_par | awk '{print $2}'`
  echo '$widthoff2' > $PAIRNAME_${rwin2}_${awin2}_widthoff.txt
  widthoff3=`grep range_samples $PAIRNAME_${rwin3}_${awin3}.off_par | awk '{print $2}'`
  echo '$widthoff3' > $PAIRNAME_${rwin3}_${awin3}_widthoff.txt
  widthoff4=`grep range_samples $PAIRNAME_${rwin4}_${awin4}.off_par | awk '{print $2}'`
  echo '$widthoff4' > $PAIRNAME_${rwin4}_${awin4}_widthoff.txt
  widthoff5=`grep range_samples $PAIRNAME_${rwin5}_${awin5}.off_par | awk '{print $2}'`
  echo '$widthoff5' > $PAIRNAME_${rwin5}_${awin5}_widthoff.txt
  
  # make SNR maps
  exec_cmd float_math ccp_${rwin1}_${awin1} ccs_${rwin1}_${awin1} SNR_${rwin1}_${awin1} $widthoff1 3 show
  exec_cmd float_math ccp_${rwin1}_${awin1} ccs_${rwin1}_${awin1} SNR_${rwin1}_${awin1} $widthoff2 3 show
  exec_cmd float_math ccp_${rwin1}_${awin1} ccs_${rwin1}_${awin1} SNR_${rwin1}_${awin1} $widthoff3 3 show
  exec_cmd float_math ccp_${rwin1}_${awin1} ccs_${rwin1}_${awin1} SNR_${rwin1}_${awin1} $widthoff4 3 show
  exec_cmd float_math ccp_${rwin1}_${awin1} ccs_${rwin1}_${awin1} SNR_${rwin1}_${awin1} $widthoff5 3 show

#  # extract slant range and azimuth offsets
#   cpx_to_real disp${rwin}_coffs rdisp$rwin $widthoff 0 show
#   cpx_to_real disp${rwin}_coffs azidisp$rwin $widthoff 1 show

# make geocoded and geotiff tiles if needed!
#   # geocode results (still needed?)
#   exec_cmd geocode_back rdisp$rwin $widthoff ${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc ${PAIRNAME}_rdisp$rwin.gc $map_width - show
#   exec_cmd geocode_back azidisp$rwin $widthoff ${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc ${PAIRNAME}_azidisp$rwin.gc $map_width - show
#   exec_cmd geocode_back ccp$rwin $widthoff ${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc ${PAIRNAME}_ccp$rwin.gc $map_width - show
#   exec_cmd geocode_back ccs$rwin $widthoff ${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc ${PAIRNAME}_ccs$rwin.gc $map_width - show
#   exec_cmd geocode_back SNR$rwin $widthoff ${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc ${PAIRNAME}_SNR$rwin.gc $map_width - show

#   # convert to geotiff (still needed?)
#   exec_cmd data2geotiff  ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ${PAIRNAME}_rdisp$rwin.gc 2 ${PAIRNAME}_rdisp$rwin.gc.tif show
#   exec_cmd data2geotiff  ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ${PAIRNAME}_azidisp$rwin.gc 2 ${PAIRNAME}_azidisp$rwin.gc.tif show
#   exec_cmd data2geotiff ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ${PAIRNAME}_ccp$rwin.gc 2 ${PAIRNAME}_ccp$rwin.gc.tif show
#   exec_cmd data2geotiff ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ${PAIRNAME}_ccs$rwin.gc 2 ${PAIRNAME}_ccs$rwin.gc.tif show
#   exec_cmd data2geotiff ${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ${PAIRNAME}_SNR$rwin.gc 2 ${PAIRNAME}_SNR$rwin.gc.tif show

  # move results
  echo "$script_name step 7: move files to storage folders"
  # offset geotiffs (not used)
#   mv ./${PAIRNAME}_rdisp$rwin.gc.tif ../OFFSETS/
#   mv ./${PAIRNAME}_azidisp$rwin.gc.tif ../OFFSETS/
#   # offset binary files (not used)
#   mv ./rdisp$rwin ../OFFSETS/${PAIRNAME}_rdisp$rwin
#   mv ./azidisp$rwin ../OFFSETS/${PAIRNAME}_azidisp$rwin
#   # ccp,ccs,SNR geotiffs (not used)
#   mv ./*_ccp$rwin.gc.tif ../CCP_CCS/${PAIRNAME}_ccp$rwin.gc.tif
#   mv ./*_ccs$rwin.gc.tif ../CCP_CCS/${PAIRNAME}_ccs$rwin.gc.tif
#   mv ./*_SNR$rwin.gc.tif ../CCP_CCS/${PAIRNAME}_SNR$rwin.gc.tif

  # ccp,ccs,SNR binary (only ccs used for now)
  mv ./ccs_${rwin1}_${awin1} ../CCP_CCS/${PAIRNAME}_ccs_${rwin1}_${awin1}
  mv ./ccs_${rwin2}_${awin2} ../CCP_CCS/${PAIRNAME}_ccs_${rwin2}_${awin2}
  mv ./ccs_${rwin3}_${awin3} ../CCP_CCS/${PAIRNAME}_ccs_${rwin3}_${awin3}
  mv ./ccs_${rwin4}_${awin4} ../CCP_CCS/${PAIRNAME}_ccs_${rwin4}_${awin4}
  mv ./ccs_${rwin5}_${awin5} ../CCP_CCS/${PAIRNAME}_ccs_${rwin5}_${awin5}

  mv ./ccp_${rwin1}_${awin1} ../CCP_CCS/${PAIRNAME}_ccp_${rwin1}_${awin1}
  mv ./ccp_${rwin2}_${awin2} ../CCP_CCS/${PAIRNAME}_ccp_${rwin2}_${awin2}
  mv ./ccp_${rwin3}_${awin3} ../CCP_CCS/${PAIRNAME}_ccp_${rwin3}_${awin3}
  mv ./ccp_${rwin4}_${awin4} ../CCP_CCS/${PAIRNAME}_ccp_${rwin4}_${awin4}
  mv ./ccp_${rwin5}_${awin5} ../CCP_CCS/${PAIRNAME}_ccp_${rwin5}_${awin5}

  mv ./SNR_${rwin1}_${awin1} ../CCP_CCS/${PAIRNAME}_SNR_${rwin1}_${awin1}
  mv ./SNR_${rwin2}_${awin2} ../CCP_CCS/${PAIRNAME}_SNR_${rwin2}_${awin2}
  mv ./SNR_${rwin3}_${awin3} ../CCP_CCS/${PAIRNAME}_SNR_${rwin3}_${awin3}
  mv ./SNR_${rwin4}_${awin4} ../CCP_CCS/${PAIRNAME}_SNR_${rwin4}_${awin4}
  mv ./SNR_${rwin5}_${awin5} ../CCP_CCS/${PAIRNAME}_SNR_${rwin5}_${awin5}

  mv ./$PAIRNAME_${rwin1}_${awin1}_widthoff.txt ../CCP_CCS/$PAIRNAME_${rwin1}_${awin1}_widthoff.txt
  mv ./$PAIRNAME_${rwin2}_${awin2}_widthoff.txt ../CCP_CCS/$PAIRNAME_${rwin2}_${awin2}_widthoff.txt
  mv ./$PAIRNAME_${rwin3}_${awin3}_widthoff.txt ../CCP_CCS/$PAIRNAME_${rwin3}_${awin3}_widthoff.txt
  mv ./$PAIRNAME_${rwin4}_${awin4}_widthoff.txt ../CCP_CCS/$PAIRNAME_${rwin4}_${awin4}_widthoff.txt
  mv ./$PAIRNAME_${rwin5}_${awin5}_widthoff.txt ../CCP_CCS/$PAIRNAME_${rwin5}_${awin5}_widthoff.txt
  # offset and ccp in text (used)
  mv ./disp_${rwin1}_${awin1}.txt ../DISP_TXT/${PAIRNAME}_disp_${rwin1}_${awin1}.txt
  mv ./disp_${rwin2}_${awin2}.txt ../DISP_TXT/${PAIRNAME}_disp_${rwin2}_${awin2}.txt
  mv ./disp_${rwin3}_${awin3}.txt ../DISP_TXT/${PAIRNAME}_disp_${rwin3}_${awin3}.txt
  mv ./disp_${rwin4}_${awin4}.txt ../DISP_TXT/${PAIRNAME}_disp_${rwin4}_${awin4}.txt
  mv ./disp_${rwin5}_${awin5}.txt ../DISP_TXT/${PAIRNAME}_disp_${rwin5}_${awin5}.txt

  # remove everything else
  echo "$script_name step 8: remove other files"
  shopt -s extglob
  rm !(*.log) # removes everything but the .log files
  # possible way to remove files apart from multiple wildcard conditions
  # GLOBIGNORE=*.log:*.txt
  # rm ./*
  # unset  GLOBIGNORE

