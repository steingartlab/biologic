ocv_params = {
    'exp_id': 'brix2/test/test',
    'steps': {
        'OCV': {
            'Rest_time_T': 3.0,
            'Record_every_dT': 1.0,
            }
        }
    }

cp_params = {
    'exp_id': 'brix2/test/test',
    'steps':
        {
            'OCV1': {
                'Rest_time_T': 3.0,
                },
            'CPLIMIT1':
                {
                    'Current_step': -1.0,
                    'N_Cycles': 0,
                    'Step_number': 0,
                    'Duration_step': 3.0,
                    'Voltage_limit': 2.7,
                    'Exit_Cond': 1
                    },
            'OCV2': {
                'Rest_time_T': 3.0,
                },
            'CPLIMIT2':
                {
                    'Current_step': 1.0,
                    'N_Cycles': 0,
                    'Step_number': 0,
                    'Duration_step': 3.0,
                    'Voltage_limit': 3.2,
                    'Exit_Cond': 1
                    },
            'LOOP':
                {
                    # loop_N_times=1 means repeat loop once, i.e. do two loops total.
                    'loop_N_times': 1,
                    # Equivalent to go to technique no 0
                    'protocol_number': 0
                    }
            }
    }

dummy_raw_data = {
    'State': 0,
    'MemFilled': 0,
    'TimeBase': 9.999999747378752e-05,
    'Ewe': 3.1290981769561768,
    'EweRangeMin': -5.0,
    'EweRangeMax': 5.0,
    'Ece': 3.423677117098123e-05,
    'EceRangeMin': -2.5,
    'EceRangeMax': 2.5,
    'Eoverflow': 0,
    'I': 0.0,
    'IRange': 0,
    'Ioverflow': 0,
    'ElapsedTime': 0.0,
    'Freq': 0.0,
    'Rcomp': 0.0,
    'Saturation': 0
    }

dummy_metadata = {
    'IRQskipped': 0,
    'NbRaws': 1,
    'NbCols': 4,
    'TechniqueIndex': 0,
    'TechniqueID': 100,
    'ProcessIn--- dex': 0,
    'loop': 0,
    'StartTime': 0.0
    }

# Matches the return string format when searching for connected potentiostats.
# See section 5.1 in documentation for details.
dummy_bytes_string = b'USB$0$$$$$HCP-1005$1002$$%'
