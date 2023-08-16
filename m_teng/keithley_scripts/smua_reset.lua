-- reset smua
smua.reset()
smua.measure.autorangev = smua.AUTORANGE_ON
smua.measure.autorangei = smua.AUTORANGE_ON
-- smua.measure.autozero = smua.AUTOZERO_AUTO
smua.measure.autozero = smua.AUTOZERO_AUTO
-- smua.measure.autozero = smua.AUTOZERO_ONCE
-- set output to 0A DC
smua.source.output = smua.OUTPUT_OFF
smua.source.func = smua.OUTPUT_DCAMPS
smua.source.leveli = smua.OUTPUT_OFF
