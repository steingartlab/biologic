raw_params = {
    'exp_id': 'brix2/test/test',
    'technique': 'OCV',
    'params': {
            'duration': {
                    'ecc': ("Rest_time_T", float),
                    'value': 10.0,
                    'index': 0
        },
            'record_dt': {
                    'ecc': ("Record_every_dT", float),
                    'value': 1.0,
                    'index': 0
        },
            'E_range': {
                    'ecc': ("E_Range", int),
                    'value': 5,
                    'index': 0
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

# Matches the return string format when searching for connected potentiostats.
# See section 5.1 in documentation for details.
dummy_bytes_string = b'Ethernet$192.109.209.180$192.109.209.180$255.255.255.0$00.14.D8.01.08.6E$VMP3#0027$VMP3$0027$x$%'
