## this is a section of bash script to be inserted into SLC_PO_SBAS_prep.bash using source
## run_PO_on_pair.sh performs pixel offset tracking on an image pair using offset_pwr_tracking2
## created July 2023, Mark Bemelmans, Bristol
  script_name='run_PO_on_pair ($ORBIT_ref $ORBIT_sec)'
  echo "$script_name step 4: coregister SLC with DEM (only if RSLC does not excist yet)"
  echo "rwin: $rwin azwin: $azwin slc_rwin: $slc_rwin1 slc_azwin: $slc_azwin1"

  ## only create RSLC if they don't excist already ##
  echo "$script_name generate pair $ORBIT_ref $ORBIT_sec"
  if [ ! -f "./RSLC/${ORBIT_ref}.rslc" ]; then
    exec_cmd slc_coreg_with_dem_v3_v2 $COMMON_ref $ORBIT_ref $DEM $DEM_PAR $demlat $demlon $RLKS $ALKS show
  fi

  if [ ! -f "./RSLC/${ORBIT_sec}.rslc" ]; then
    exec_cmd slc_coreg_with_dem_v3_v2 $COMMON_ref $ORBIT_sec $DEM $DEM_PAR $demlat $demlon $RLKS $ALKS show
  fi

  ## MAKE NEW IMAGE PAIR FOLDER ##
  PAIRNAME=${ORBIT_ref}_${ORBIT_sec}
  cd ./PO_SBAS_PAIRS

  if [ -d "$PAIRNAME" ]; then
    rm -rf $PAIRNAME
  fi

  if [ ! -d "$PAIRNAME" ]; then
    mkdir $PAIRNAME
  fi
  cd $PAIRNAME

  ## MAKE SYMLINKS TO REQUIRED FILES ##
  ln -s ../../RSLC/$ORBIT_ref.rslc ./$ORBIT_ref.rslc 
  ln -s ../../RSLC/$ORBIT_ref.rslc.par ./$ORBIT_ref.rslc.par 
  ln -s ../../RSLC/$ORBIT_sec.rslc ./$ORBIT_sec.rslc 
  ln -s ../../RSLC/$ORBIT_sec.rslc.par ./$ORBIT_sec.rslc.par 
  ln -s ../../RSLC/$COMMON_ref.rslc ./$COMMON_ref.rslc 
  ln -s ../../RSLC/$COMMON_ref.rslc.par ./$COMMON_ref.rslc.par 
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.rmli ./${COMMON_ref}_${map_rlks}_${map_alks}.rmli 
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.rmli.par ./${COMMON_ref}_${map_rlks}_${map_alks}.rmli.par 
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc ./${COMMON_ref}_${map_rlks}_${map_alks}.map_to_rdc 
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg ./${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg 
  ln -s ../../PO_geocoding/${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par ./${COMMON_ref}_${map_rlks}_${map_alks}.dem_seg.par 

  ## perform Pixel Offset Tracking wiht cropping ##
  if [ $cropping_flag == 1 ]; then
    # crop RSLCs
    exec_cmd SLC_copy $COMMON_ref.rslc $COMMON_ref.rslc.par $COMMON_ref.crop.rslc $COMMON_ref.crop.rslc.par 4 - $rstart $n_samples_crop $astart $n_lines_crop - - show
    exec_cmd SLC_copy $ORBIT_ref.rslc $ORBIT_ref.rslc.par $ORBIT_ref.crop.rslc $ORBIT_ref.crop.rslc.par 4 - $rstart $n_samples_crop $astart $n_lines_crop - - show
    exec_cmd SLC_copy $ORBIT_sec.rslc $ORBIT_sec.rslc.par $ORBIT_sec.crop.rslc $ORBIT_sec.crop.rslc.par 4 - $rstart $n_samples_crop $astart $n_lines_crop - - show
  
    # create initial offset par file
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par ${PAIRNAME}_${init_rwin}_${init_awin}.off_par_init 1 1 1 0 show
  
    echo "$script_name step 5: offset tracking with initial large window size (e.g., 256-by-256)"
    exec_cmd offset_pwr $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par ${PAIRNAME}_${init_rwin}_${init_awin}.off_par_init offs_${init_rwin}_${init_awin} ccp_${init_rwin}_${init_awin} $init_rwin $init_awin offsets_${init_rwin}_${init_awin}.txt - - - $ccpthresh 9 - - - show
    exec_cmd offset_fit offs_${init_rwin}_${init_awin} ccp_${init_rwin}_${init_awin} ${PAIRNAME}_${init_rwin}_${init_awin}.off_par_init coffs_${init_rwin}_${init_awin} coffsets_${init_rwin}_${init_awin}.txt $ccpthresh 4 0 show


    # create off_par for windwo sizes going dow
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par 1 1 1 0 show
    exec_cmd create_offset $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par 1 1 1 0 show
  
  
    # calculate window size dependent on multi-looking values
    if [ $step_win_flag == 0 ]; then
        let slc_rwin1=rwin1*RLKS
        let slc_awin1=azwin1*ALKS

        let slc_rwin2=rwin2*RLKS
        let slc_awin2=azwin2*ALKS

        let slc_rwin3=rwin3*RLKS
        let slc_awin3=azwin3*ALKS

        let slc_rwin4=rwin4*RLKS
        let slc_awin4=azwin4*ALKS

        let slc_rwin5=rwin5*RLKS
        let slc_awin5=azwin5*ALKS
    fi

    # make multiple window size pixel offsets
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin1 azwin: $azwin1 slc_rwin: $slc_rwin1 slc_azwin: $slc_azwin1"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par offs_${slc_rwin1}_${slc_awin1} ccp_${slc_rwin1}_${slc_awin1} \
                                  ${PAIRNAME}_${init_rwin}_${init_awin}.off_par_init offs_${init_rwin}_${init_awin} \
                                  $slc_rwin1 $slc_awin1 offsets_${slc_rwin1}_${slc_awin1}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin1}_${slc_awin1} show
  
    exec_cmd offset_fit offs_${slc_rwin1}_${slc_awin1} ccp_${slc_rwin1}_${slc_awin1} ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par coffs_${slc_rwin1}_${slc_awin1} coffsets_${slc_rwin1}_${slc_awin1}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin1}_${slc_awin1} ccp_${slc_rwin1}_${slc_awin1} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par disp_${slc_rwin1}_${slc_awin1}_coffs disp_${slc_rwin1}_${slc_awin1}.txt 1 $final_cpthresh 1 show

    #rwin2
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin2 azwin: $azwin2 slc_rwin: $slc_rwin2 slc_azwin: $slc_azwin2"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par offs_${slc_rwin2}_${slc_awin2} ccp_${slc_rwin2}_${slc_awin2} \
                                  ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par offs_${slc_rwin1}_${slc_awin1} \
                                  $slc_rwin2 $slc_awin2 offsets_${slc_rwin2}_${slc_awin2}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin2}_${slc_awin2} show
  
    exec_cmd offset_fit offs_${slc_rwin2}_${slc_awin2} ccp_${slc_rwin2}_${slc_awin2} ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par coffs_${slc_rwin2}_${slc_awin2} coffsets_${slc_rwin2}_${slc_awin2}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin2}_${slc_awin2} ccp_${slc_rwin2}_${slc_awin2} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par disp_${slc_rwin2}_${slc_awin2}_coffs disp_${slc_rwin2}_${slc_awin2}.txt 1 $final_cpthresh 1 show

    #rwin3
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin3 azwin: $azwin3 slc_rwin: $slc_rwin3 slc_azwin: $slc_azwin3"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par offs_${slc_rwin3}_${slc_awin3} ccp_${slc_rwin3}_${slc_awin3} \
                                  ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par offs_${slc_rwin2}_${slc_awin2} \
                                  $slc_rwin3 $slc_awin3 offsets_${slc_rwin3}_${slc_awin3}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin3}_${slc_awin3} show

    exec_cmd offset_fit offs_${slc_rwin3}_${slc_awin3} ccp_${slc_rwin3}_${slc_awin3} ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par coffs_${slc_rwin3}_${slc_awin3} coffsets_${slc_rwin3}_${slc_awin3}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin3}_${slc_awin3} ccp_${slc_rwin3}_${slc_awin3} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par disp_${slc_rwin3}_${slc_awin3}_coffs disp_${slc_rwin3}_${slc_awin3}.txt 1 $final_cpthresh 1 show

    #rwin4
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin4 azwin: $azwin4 slc_rwin: $slc_rwin4 slc_azwin: $slc_azwin4"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par offs_${slc_rwin4}_${slc_awin4} ccp_${slc_rwin4}_${slc_awin4} \
                                  ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par offs_${slc_rwin3}_${slc_awin3} \
                                  $slc_rwin4 $slc_awin4 offsets_${slc_rwin4}_${slc_awin4}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin4}_${slc_awin4} show

    exec_cmd offset_fit offs_${slc_rwin4}_${slc_awin4} ccp_${slc_rwin4}_${slc_awin4} ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par coffs_${slc_rwin4}_${slc_awin4} coffsets_${slc_rwin4}_${slc_awin4}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin4}_${slc_awin4} ccp_${slc_rwin4}_${slc_awin4} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par disp_${slc_rwin4}_${slc_awin4}_coffs disp_${slc_rwin4}_${slc_awin4}.txt 1 $final_cpthresh 1 show

    #rwin5
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin5 azwin: $azwin5 slc_rwin: $slc_rwin5 slc_azwin: $slc_azwin5"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.crop.rslc $ORBIT_sec.crop.rslc $ORBIT_ref.crop.rslc.par $ORBIT_sec.crop.rslc.par \
                                  ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par offs_${slc_rwin5}_${slc_awin5} ccp_${slc_rwin5}_${slc_awin5} \
                                  ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par offs_${slc_rwin4}_${slc_awin4} \
                                  $slc_rwin5 $slc_awin5 offsets_${slc_rwin5}_${slc_awin5}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin5}_${slc_awin5} show
  
    exec_cmd offset_fit offs_${slc_rwin5}_${slc_awin5} ccp_${slc_rwin5}_${slc_awin5} ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par coffs_${slc_rwin5}_${slc_awin5} coffsets_${slc_rwin5}_${slc_awin5}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin5}_${slc_awin5} ccp_${slc_rwin5}_${slc_awin5} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par disp_${slc_rwin5}_${slc_awin5}_coffs disp_${slc_rwin5}_${slc_awin5}.txt 1 $final_cpthresh 1 show

  fi
  
  ## Perform Pixel Offset trackign without cropping ##
  if [ $cropping_flag == 0 ]; then
    # create initial offset par file
    exec_cmd create_offset ${ORBIT_ref}.rslc.par ${ORBIT_sec}.rslc.par ${PAIRNAME}_${init_rwin}_${init_awin}.off_par_init 1 1 1 0 show
  
    echo "$script_name step 5: offset tracking with initial large window size (e.g., 256-by-256)"
    exec_cmd offset_pwr ${ORBIT_ref}.rslc ${ORBIT_sec}.rslc ${ORBIT_ref}.rslc.par ${ORBIT_sec}.rslc.par ${PAIRNAME}_${init_rwin}_${init_awin}.off_par_init offs_${init_rwin}_${init_awin} ccp_${init_rwin}_${init_awin} $init_rwin $init_awin offsets_${init_rwin}_${init_awin}.txt - - - $ccpthresh 9 - - - show
    exec_cmd offset_fit offs_${init_rwin}_${init_awin} ccp_${init_rwin}_${init_awin} ${PAIRNAME}_${init_rwin}_${init_awin}.off_par_init coffs_${init_rwin}_${init_awin} coffsets_${init_rwin}_${init_awin}.txt $ccpthresh 4 0 show
    
  
    # create off_par for windwo sizes going down
    exec_cmd create_offset ${ORBIT_ref}.rslc.par ${ORBIT_sec}.rslc.par ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par 1 1 1 0 show
    exec_cmd create_offset ${ORBIT_ref}.rslc.par ${ORBIT_sec}.rslc.par ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par 1 1 1 0 show
    exec_cmd create_offset ${ORBIT_ref}.rslc.par ${ORBIT_sec}.rslc.par ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par 1 1 1 0 show
    exec_cmd create_offset ${ORBIT_ref}.rslc.par ${ORBIT_sec}.rslc.par ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par 1 1 1 0 show
    exec_cmd create_offset ${ORBIT_ref}.rslc.par ${ORBIT_sec}.rslc.par ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par 1 1 1 0 show
  
  
    # calculate window size dependent on multi-looking values
    if [ $step_win_flag == 0 ]; then
        let slc_rwin1=rwin1*RLKS
        let slc_awin1=azwin1*ALKS

        let slc_rwin2=rwin2*RLKS
        let slc_awin2=azwin2*ALKS

        let slc_rwin3=rwin3*RLKS
        let slc_awin3=azwin3*ALKS

        let slc_rwin4=rwin4*RLKS
        let slc_awin4=azwin4*ALKS

        let slc_rwin5=rwin5*RLKS
        let slc_awin5=azwin5*ALKS
    fi

        # make multiple window size pixel offsets
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin1 azwin: $azwin1 slc_rwin: $slc_rwin1 slc_azwin: $slc_azwin1"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par offs_${slc_rwin1}_${slc_awin1} ccp_${slc_rwin1}_${slc_awin1} \
                                  ${PAIRNAME}_${init_rwin}_${init_awin}.off_par_init offs_${init_rwin}_${init_awin} \
                                  $slc_rwin1 $slc_awin1 offsets_${slc_rwin1}_${slc_awin1}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin1}_${slc_awin1} show
  
    exec_cmd offset_fit offs_${slc_rwin1}_${slc_awin1} ccp_${slc_rwin1}_${slc_awin1} ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par coffs_${slc_rwin1}_${slc_awin1} coffsets_${slc_rwin1}_${slc_awin1}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin1}_${slc_awin1} ccp_${slc_rwin1}_${slc_awin1} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par disp_${slc_rwin1}_${slc_awin1}_coffs disp_${slc_rwin1}_${slc_awin1}.txt 1 $final_cpthresh 1 show

    #rwin2
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin2 azwin: $azwin2 slc_rwin: $slc_rwin2 slc_azwin: $slc_azwin2"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par offs_${slc_rwin2}_${slc_awin2} ccp_${slc_rwin2}_${slc_awin2} \
                                  ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par offs_${slc_rwin1}_${slc_awin1} \
                                  $slc_rwin2 $slc_awin2 offsets_${slc_rwin2}_${slc_awin2}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin2}_${slc_awin2} show
  
    exec_cmd offset_fit offs_${slc_rwin2}_${slc_awin2} ccp_${slc_rwin2}_${slc_awin2} ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par coffs_${slc_rwin2}_${slc_awin2} coffsets_${slc_rwin2}_${slc_awin2}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin2}_${slc_awin2} ccp_${slc_rwin2}_${slc_awin2} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par disp_${slc_rwin2}_${slc_awin2}_coffs disp_${slc_rwin2}_${slc_awin2}.txt 1 $final_cpthresh 1 show

    #rwin3
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin3 azwin: $azwin3 slc_rwin: $slc_rwin3 slc_azwin: $slc_azwin3"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par offs_${slc_rwin3}_${slc_awin3} ccp_${slc_rwin3}_${slc_awin3} \
                                  ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par offs_${slc_rwin2}_${slc_awin2} \
                                  $slc_rwin3 $slc_awin3 offsets_${slc_rwin3}_${slc_awin3}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin3}_${slc_awin3} show

    exec_cmd offset_fit offs_${slc_rwin3}_${slc_awin3} ccp_${slc_rwin3}_${slc_awin3} ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par coffs_${slc_rwin3}_${slc_awin3} coffsets_${slc_rwin3}_${slc_awin3}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin3}_${slc_awin3} ccp_${slc_rwin3}_${slc_awin3} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par disp_${slc_rwin3}_${slc_awin3}_coffs disp_${slc_rwin3}_${slc_awin3}.txt 1 $final_cpthresh 1 show

    #rwin4
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin4 azwin: $azwin4 slc_rwin: $slc_rwin4 slc_azwin: $slc_azwin4"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par offs_${slc_rwin4}_${slc_awin4} ccp_${slc_rwin4}_${slc_awin4} \
                                  ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par offs_${slc_rwin3}_${slc_awin3} \
                                  $slc_rwin4 $slc_awin4 offsets_${slc_rwin4}_${slc_awin4}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin4}_${slc_awin4} show

    exec_cmd offset_fit offs_${slc_rwin4}_${slc_awin4} ccp_${slc_rwin4}_${slc_awin4} ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par coffs_${slc_rwin4}_${slc_awin4} coffsets_${slc_rwin4}_${slc_awin4}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin4}_${slc_awin4} ccp_${slc_rwin4}_${slc_awin4} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par disp_${slc_rwin4}_${slc_awin4}_coffs disp_${slc_rwin4}_${slc_awin4}.txt 1 $final_cpthresh 1 show

    #rwin5
    echo "$script_name $ORBIT_ref $ORBIT_sec rwin: $rwin5 azwin: $azwin5 slc_rwin: $slc_rwin5 slc_azwin: $slc_azwin5"
    exec_cmd offset_pwr_tracking2 $ORBIT_ref.rslc $ORBIT_sec.rslc $ORBIT_ref.rslc.par $ORBIT_sec.rslc.par \
                                  ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par offs_${slc_rwin5}_${slc_awin5} ccp_${slc_rwin5}_${slc_awin5} \
                                  ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par offs_${slc_rwin4}_${slc_awin4} \
                                  $slc_rwin5 $slc_awin5 offsets_${slc_rwin5}_${slc_awin5}.txt 2 $ccpthresh \
                                  $map_rlks $map_alks - - - - 1.0 - - - - ccs_${slc_rwin5}_${slc_awin5} show
  
    exec_cmd offset_fit offs_${slc_rwin5}_${slc_awin5} ccp_${slc_rwin5}_${slc_awin5} ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par coffs_${slc_rwin5}_${slc_awin5} coffsets_${slc_rwin5}_${slc_awin5}.txt $ccpthresh 4 0 show
    exec_cmd offset_tracking offs_${slc_rwin5}_${slc_awin5} ccp_${slc_rwin5}_${slc_awin5} ${ORBIT_ref}.rslc.par ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par disp_${slc_rwin5}_${slc_awin5}_coffs disp_${slc_rwin5}_${slc_awin5}.txt 1 $final_cpthresh 1 show

  fi
  
  # get width of offset maps
  widthoff1=`grep range_samples ${PAIRNAME}_${slc_rwin1}_${slc_awin1}.off_par | awk '{print $2}'`
  $widthoff1 > ${PAIRNAME}_${slc_rwin1}_${slc_awin1}_widthoff.txt
  widthoff2=`grep range_samples ${PAIRNAME}_${slc_rwin2}_${slc_awin2}.off_par | awk '{print $2}'`
  $widthoff2 > ${PAIRNAME}_${slc_rwin2}_${slc_awin2}_widthoff.txt
  widthoff3=`grep range_samples ${PAIRNAME}_${slc_rwin3}_${slc_awin3}.off_par | awk '{print $2}'`
  $widthoff3 > ${PAIRNAME}_${slc_rwin3}_${slc_awin3}_widthoff.txt
  widthoff4=`grep range_samples ${PAIRNAME}_${slc_rwin4}_${slc_awin4}.off_par | awk '{print $2}'`
  $widthoff4 > ${PAIRNAME}_${slc_rwin4}_${slc_awin4}_widthoff.txt
  widthoff5=`grep range_samples ${PAIRNAME}_${slc_rwin5}_${slc_awin5}.off_par | awk '{print $2}'`
  $widthoff5 > ${PAIRNAME}_${slc_rwin5}_${slc_awin5}_widthoff.txt
  
  # make SNR maps
  exec_cmd float_math ccp_${slc_rwin1}_${slc_awin1} ccs_${slc_rwin1}_${slc_awin1} SNR_${slc_rwin1}_${slc_awin1} $widthoff1 3 show
  exec_cmd float_math ccp_${slc_rwin2}_${slc_awin2} ccs_${slc_rwin2}_${slc_awin2} SNR_${slc_rwin2}_${slc_awin2} $widthoff2 3 show
  exec_cmd float_math ccp_${slc_rwin3}_${slc_awin3} ccs_${slc_rwin3}_${slc_awin3} SNR_${slc_rwin3}_${slc_awin3} $widthoff3 3 show
  exec_cmd float_math ccp_${slc_rwin4}_${slc_awin4} ccs_${slc_rwin4}_${slc_awin4} SNR_${slc_rwin4}_${slc_awin4} $widthoff4 3 show
  exec_cmd float_math ccp_${slc_rwin5}_${slc_awin5} ccs_${slc_rwin5}_${slc_awin5} SNR_${slc_rwin5}_${slc_awin5} $widthoff5 3 show


  # move results
  echo "$script_name step 7: move files to storage folders"

  # ccp,ccs,SNR binary (only ccs used for now)
  mv ./ccs_${slc_rwin1}_${slc_awin1} ../CCP_CCS/${PAIRNAME}_ccs_${slc_rwin1}_${slc_awin1}
  mv ./ccs_${slc_rwin2}_${slc_awin2} ../CCP_CCS/${PAIRNAME}_ccs_${slc_rwin2}_${slc_awin2}
  mv ./ccs_${slc_rwin3}_${slc_awin3} ../CCP_CCS/${PAIRNAME}_ccs_${slc_rwin3}_${slc_awin3}
  mv ./ccs_${slc_rwin4}_${slc_awin4} ../CCP_CCS/${PAIRNAME}_ccs_${slc_rwin4}_${slc_awin4}
  mv ./ccs_${slc_rwin5}_${slc_awin5} ../CCP_CCS/${PAIRNAME}_ccs_${slc_rwin5}_${slc_awin5}

  mv ./ccp_${slc_rwin1}_${slc_awin1} ../CCP_CCS/${PAIRNAME}_ccp_${slc_rwin1}_${slc_awin1}
  mv ./ccp_${slc_rwin2}_${slc_awin2} ../CCP_CCS/${PAIRNAME}_ccp_${slc_rwin2}_${slc_awin2}
  mv ./ccp_${slc_rwin3}_${slc_awin3} ../CCP_CCS/${PAIRNAME}_ccp_${slc_rwin3}_${slc_awin3}
  mv ./ccp_${slc_rwin4}_${slc_awin4} ../CCP_CCS/${PAIRNAME}_ccp_${slc_rwin4}_${slc_awin4}
  mv ./ccp_${slc_rwin5}_${slc_awin5} ../CCP_CCS/${PAIRNAME}_ccp_${slc_rwin5}_${slc_awin5}

  mv ./SNR_${slc_rwin1}_${slc_awin1} ../CCP_CCS/${PAIRNAME}_SNR_${slc_rwin1}_${slc_awin1}
  mv ./SNR_${slc_rwin2}_${slc_awin2} ../CCP_CCS/${PAIRNAME}_SNR_${slc_rwin2}_${slc_awin2}
  mv ./SNR_${slc_rwin3}_${slc_awin3} ../CCP_CCS/${PAIRNAME}_SNR_${slc_rwin3}_${slc_awin3}
  mv ./SNR_${slc_rwin4}_${slc_awin4} ../CCP_CCS/${PAIRNAME}_SNR_${slc_rwin4}_${slc_awin4}
  mv ./SNR_${slc_rwin5}_${slc_awin5} ../CCP_CCS/${PAIRNAME}_SNR_${slc_rwin5}_${slc_awin5}

  mv ./${PAIRNAME}_${slc_rwin1}_${slc_awin1}_widthoff.txt ../CCP_CCS/${PAIRNAME}_${slc_rwin1}_${slc_awin1}_widthoff.txt
  mv ./${PAIRNAME}_${slc_rwin2}_${slc_awin2}_widthoff.txt ../CCP_CCS/${PAIRNAME}_${slc_rwin2}_${slc_awin2}_widthoff.txt
  mv ./${PAIRNAME}_${slc_rwin3}_${slc_awin3}_widthoff.txt ../CCP_CCS/${PAIRNAME}_${slc_rwin3}_${slc_awin3}_widthoff.txt
  mv ./${PAIRNAME}_${slc_rwin4}_${slc_awin4}_widthoff.txt ../CCP_CCS/${PAIRNAME}_${slc_rwin4}_${slc_awin4}_widthoff.txt
  mv ./${PAIRNAME}_${slc_rwin5}_${slc_awin5}_widthoff.txt ../CCP_CCS/${PAIRNAME}_${slc_rwin5}_${slc_awin5}_widthoff.txt
  # offset and ccp in text (used)
  mv ./disp_${slc_rwin1}_${slc_awin1}.txt ../DISP_TXT/${PAIRNAME}_disp_${slc_rwin1}_${slc_awin1}.txt
  mv ./disp_${slc_rwin2}_${slc_awin2}.txt ../DISP_TXT/${PAIRNAME}_disp_${slc_rwin2}_${slc_awin2}.txt
  mv ./disp_${slc_rwin3}_${slc_awin3}.txt ../DISP_TXT/${PAIRNAME}_disp_${slc_rwin3}_${slc_awin3}.txt
  mv ./disp_${slc_rwin4}_${slc_awin4}.txt ../DISP_TXT/${PAIRNAME}_disp_${slc_rwin4}_${slc_awin4}.txt
  mv ./disp_${slc_rwin5}_${slc_awin5}.txt ../DISP_TXT/${PAIRNAME}_disp_${slc_rwin5}_${slc_awin5}.txt

  # remove everything else
  echo "$script_name step 8: remove other files"
  shopt -s extglob
  rm !(*.log) # removes everything but the .log files
  # possible way to remove files apart from multiple wildcard conditions
  # GLOBIGNORE=*.log:*.txt
  # rm ./*
  # unset  GLOBIGNORE
  shopt -u extglob

