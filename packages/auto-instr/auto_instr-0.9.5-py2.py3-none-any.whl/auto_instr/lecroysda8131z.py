from time import sleep

# Go to Utilities> UtilitiesSetup> Remote and select the LXI (VXI-11) setting. Note the
# oscilloscope's IP address.


class lecroy_scope(object):
    
    def default_setup(instr):
        instr.timeout = 5000
        instr.clear()
        #checks
        instr.write("COMM_HEADER OFF")
        instr.write(r"""vbs 'app.settodefaultsetup' """)
        r = instr.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        #acquisitions setup
        instr.write(r"""vbs 'app.acquisition.trigger.edge.level = <value>' """)
        instr.write(r"""vbs 'app.acquisition.triggermode = "single" ' """)
        instr.write(r"""vbs 'app.acquisition.horizontal.maximize = "<value>" ' """)
        #measurement setup
        instr.write(r"""vbs 'app.measure.clearall ' """)
        instr.write(r"""vbs 'app.measure.clearsweeps ' """)

        instr.write(r"""vbs 'app.measure.showmeasure = true ' """)
        instr.write(r"""vbs 'app.measure.statson = true ' """)
        instr.write(r"""vbs 'app.measure.p1.view = true ' """)
        instr.write(r"""vbs 'app.measure.p1.paramengine = "<value>" ' """)
        instr.write(r"""vbs 'app.measure.p1.source1 = "C1" ' """)

        #acquire
        for i in range(0,10):
            r = instr.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
            r = instr.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
            if r==0:
                print("Time out from WaitUntilIdle, return = {0}".format(r))

        # read
        var  = instr.query(r"""vbs? 'return=app.measure.p1.out.result.value' """)
        print ("<var> = {0}".format(var))
        instr.close()


############ Channel settings ####################

    def channel_offset(instr,ch_no, v_offset):
        instr.write(r"""vbs 'app.Acquisition.C%i.VerOffset = %f ' """ %(ch_no, v_offset))

    def channel_scale(instr,ch_no, v_scale):
        instr.write(r"""vbs 'app.Acquisition.C%i.VerScale = %f ' """ % (ch_no, v_scale))

    def horz_scale(instr,scale):
        instr.write(r"""vbs 'app.Acquisition.Horizontal.HorScale = %f ' """ % (scale))

    def bandwidth_full(instr,ch_no):
        instr.write(r"""vbs 'app.Acquisition.C%i.BandwidthLimit = %s ' """ %(ch_no,'FULL'))

    def set_bandwidth(instr,ch_no,bw ='200MHz'): #20MHz pass string only
        instr.write(r"""vbs 'app.Acquisition.C%i.BandwidthLimit = %s ' """ % (ch_no, bw))

    def autoset(instr):
        instr.write(r"""vbs 'app.AutoSetup ' """)
        r = instr.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        if r == 0:
            print("Time out from WaitUntilIdle, return = {0}".format(r))

    def set_abs_ref_lev(instr,abs_min_ref_lev,abs_max_ref_lev):
        instr.write('MEASU:IMM:REFL:METH ABS')
        instr.write('MEASU:IMM:REFL:ABS:HIGH %f' % abs_max_ref_lev)
        instr.write('MEASU:IMM:REFL:ABS:LOW %f' % abs_min_ref_lev)

    def set_perc_ref_lev(instr,perc_min_ref_lev=10,perc_max_ref_lev=90):
        instr.write('MEASU:IMM:REFL:METH PERC')
        instr.write('MEASU:IMM:REFL:PERC:HIGH %f' % perc_max_ref_lev)
        instr.write('MEASU:IMM:REFL:PERC:LOW %f' % perc_min_ref_lev)

    def set_abs_mid_ref_lev(instr, abs_mid1_ref_lev,abs_mid2_ref_lev):
        instr.write('MEASU:IMM:REFL:METH ABS')
        instr.write('MEASU:IMM:REFL:ABS:MID1 %f' % abs_mid1_ref_lev)
        instr.write('MEASU:IMM:REFL:ABS:MID2 %f' % abs_mid2_ref_lev)

    def set_perc_mid_ref_lev(instr,perc_mid1_ref_lev=50,perc_mid2_ref_lev=50):
        instr.write('MEASU:IMM:REFL:METH PERC')
        instr.write('MEASU:IMM:REFL:PERC:MID1 %f' % perc_mid1_ref_lev)
        instr.write('MEASU:IMM:REFL:PERC:MID2 %f' % perc_mid2_ref_lev)

############ Acquisition modes ########################
    def clear(instr):
        instr.write('CLEAR')

    def run(instr):
        instr.write('ACQ:STATE RUN')

    def stop(instr):
        instr.write('ACQ:STATE STOP')

    def run_mode(instr):
        instr.write('ACQ:STOPA RUNST')

    def single(instr):
        instr.write('ACQ:STOPA SEQ')

    def single_refresh(instr):
        instr.write('ACQ:STATE ON')

    def averaging(instr,no_avg):
        instr.write('ACQ:MOD AVE')
        instr.write('ACQ:NUMAV %i'%no_avg)

    def high_resolution(instr):
        instr.write('ACQ:MOD HIR')

############### Measurement functions #############

    def meas_cls(instr):
        instr.write('MEASU:STATI:COUN RESET')

    def measure_source(instr,ch_no):
        instr.write('MEASU:IMM:SOU1 CH%i' %ch_no)

    def measure_amp(instr):
        instr.write('MEASU:IMM:TYP AMP')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_high(instr):
        instr.write('MEASU:IMM:TYP HIGH')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_low(instr):
        instr.write('MEASU:IMM:TYP LOW')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_freq(instr):
        instr.write('MEASU:IMM:TYP FREQ')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_positive_duty(instr):
        instr.write('MEASU:IMM:TYP PDU')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_negative_duty(instr):
        instr.write('MEASU:IMM:TYP NDU')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_rise_time(instr):
        instr.write('MEASU:IMM:TYP RIS')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_fall_time(instr):
        instr.write('MEASU:IMM:TYP FALL')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_positive_pulse_width(instr):
        instr.write('MEASU:IMM:TYP PWI')
        return float(instr.query('MEASU:IMM:VAL?'))

    def measure_negative_pulse_width(instr):
        instr.write('MEASU:IMM:TYP NWI')
        return float(instr.query('MEASU:IMM:VAL?'))

    def export_screenshot(instr,filename):
        instr.write('EXP:FILEN ' + '\"' + filename + '.PNG' + '\"')
        instr.write('EXP STAR')
        instr.write('EXP:FOR PNG')

 ############### Cursor functions ############

    def horizontal_curser(instr):
        instr.write('CURS:HBA:POSITION1 6.2')

    def source_cursor(instr):
        instr.write('CURSOR:SOURCE 1 CH2')

    def vertical_bar_position_query(instr):
        return str(instr.query('CURSor:VBArs?'))

    def diff_between_vericalbar(instr):
        return float(instr.query('CURSOR:VBARS:DELTA?'))
 
 ############### trigger functions ##################
    def trigger_auto_mode(instr):
        instr.write(r"""vbs 'app.Acquisition.TriggerMode = %s ' """ % ('Auto'))
    def trigger_stop_mode(instr):
        instr.write(r"""vbs 'app.Acquisition.TriggerMode = %s ' """ % ('Stopped'))
    def trigger_single_mode(instr):
        instr.write(r"""vbs 'app.Acquisition.TriggerMode = %s ' """ % ('Single'))
    def trigger_normal_mode(instr):
        instr.write(r"""vbs 'app.Acquisition.TriggerMode = %s ' """ % ('Normal'))
    # def trigger_source(instr,channel_no=1):
    #     instr.write(r"""vbs 'app.Acquisition.Trigger.C%i' """ %channel_no )
    def save_waveform_csv(instr):
        instr.write(r"""vbs 'app.SaveRecall.Waveform.SaveTo = "%s"' """ % ('File'))
        instr.write(r"""vbs 'app.SaveRecall.Waveform.SaveSource = "%s"' """ % ('C1'))
        instr.write(r"""vbs 'app.SaveRecall.Waveform.WaveformDir = "%s"' """ % (r'D:\vind'))
        instr.write(r"""vbs 'app.SaveRecall.Waveform.TraceTitle = "%s"' """ % (r'test'))
        instr.write(r"""vbs 'app.SaveRecall.Waveform.WaveFormat = "%s"' """ % ('Excel'))
        instr.write(r"""vbs 'app.SaveRecall.Waveform.Delimiter = "%s"' """ % ('Comma'))
        instr.write(r"""vbs 'app.SaveRecall.Waveform.DoSave""")

    def trigger_level(instr, ch_no, lev):
        instr.write('TRIG:A:LEV:CH%i %f' %(ch_no, lev))

    def trigger_level_query(instr,ch_no):
        return float(instr.query('TRIG:A:LEV:CH%i?' %ch_no))
    
    def trigger_quickset(instr, ch_no,lev):
        instr.write('TRIG:A:EDGE:SOU CH%i' %ch_no)
        instr.write('TRIG:A:EDGE:SLO:CH%i RIS' % ch_no)
        instr.write('TRIG:A:LEV:CH%i %f' %(ch_no, lev))

    def trigger_quickset_rise(instr, ch_no,lev):
        instr.write('TRIG:A:EDGE:SOU CH%i' %ch_no)
        instr.write('TRIG:A:EDGE:SLO:CH%i RIS' % ch_no)
        instr.write('TRIG:A:LEV:CH%i %f' %(ch_no, lev))

    def trigger_quickset_fall(instr, ch_no,lev):
        instr.write('TRIG:A:EDGE:SOU CH%i' %ch_no)
        instr.write('TRIG:A:EDGE:SLO:CH%i FALL' % ch_no)
        instr.write('TRIG:A:LEV:CH%i %f' %(ch_no, lev))

    def single_acquisition_quickset(instr,ch_no,lev,edge='RISE'): #use FALL for falling egde trigger
        scope.run(instr)
        if edge =='FALL':
            scope.trigger_quickset_fall(instr, ch_no,lev)
        else:
            scope.trigger_quickset_rise(instr, ch_no, lev)
        scope.meas_cls(instr)
        scope.single(instr)

    def scope_trig_pulsewidth(instr,ch_no,lev,upperlimit,lowerlimit):
        instr.write('ACQ:STATE RUN')
        instr.write('ACQ:STATE ON')
        instr.write('ACQ:STOPA RUNST')
        instr.write('TRIG:A:PUL:SOU CH%i ' % ch_no)
        instr.write('TRIG:A:PUL:CLA WID')
        instr.write('TRIG:A:PUL:WIDTH:LOWLIMIT %f' % lowerlimit)
        instr.write('TRIG:A:PUL:WIDTH:HIGHLIMIT %f' % upperlimit)
        instr.write('TRIG:A:LEV:CH%i %f' % (ch_no, lev))
        instr.write('TRIG:A:PUL:WIDTH:POL POSITIVE')
        instr.write('TRIG:A:PUL:WIDTH:QUAL OCC')
        instr.write('TRIG:A:PUL:WIDTH:WHE WIT')
        instr.write('MEASU:STATI:COUN RESET')
        instr.write('ACQ:STOPA SEQ')

    def lecroy_scope_eUSB_rise_fall_time(instr):
        instr.write(r"""vbs 'app.measure.clearall ' """)
        instr.write(r"""vbs 'app.measure.showmeasure = true ' """)
        instr.write(r"""vbs 'app.measure.statson = true ' """)
        instr.write(r"""vbs 'app.measure.p1.view = true ' """)
        instr.write(r"""vbs 'app.measure.p1.paramengine = "rise" ' """)
        instr.write(r"""vbs 'app.measure.p1.source1 = "C1" ' """)
        instr.write(r"""vbs 'app.measure.p2.view = true ' """)
        instr.write(r"""vbs 'app.measure.p2.paramengine = "fall" ' """)
        instr.write(r"""vbs 'app.measure.p2.source1 = "C1" ' """)
        instr.write(r"""vbs 'app.measure.p3.view = true ' """)
        instr.write(r"""vbs 'app.measure.p3.paramengine = "rise2080" ' """)
        instr.write(r"""vbs 'app.measure.p3.source1 = "C1" ' """)
        instr.write(r"""vbs 'app.measure.p4.view = true ' """)
        instr.write(r"""vbs 'app.measure.p4.paramengine = "fall8020" ' """)
        instr.write(r"""vbs 'app.measure.p4.source1 = "C1" ' """)
        sleep(20)
        # for i in range(0, 10):
        #     r = instr.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
        #     r = instr.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        # if r == 0:
        #     print("Time out from WaitUntilIdle, return = {0}".format(r))

        try:
            tr1090 = float(((instr.query(r"""vbs? 'return=app.measure.p1.mean.result.value' """)).split(' '))[1])
            tf9010 = float(((instr.query(r"""vbs? 'return=app.measure.p2.mean.result.value' """)).split(' '))[1])
            tr2080 = float(((instr.query(r"""vbs? 'return=app.measure.p3.mean.result.value' """)).split(' '))[1])
            tf8020 = float(((instr.query(r"""vbs? 'return=app.measure.p4.mean.result.value' """)).split(' '))[1])
        except:
            tr1090 = 'NA'
            tf9010 = 'NA'
            tr2080 = 'NA'
            tf8020 = 'NA'
        return [tr1090, tf9010, tr2080, tf8020]


