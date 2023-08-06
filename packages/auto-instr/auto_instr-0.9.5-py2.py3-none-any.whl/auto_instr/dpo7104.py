from time import sleep
class scope(object):

############ Channel settings ####################

    def channel_offset(instr,ch_no, v_offset):
        instr.write('CH%i:OFFS %f' % (ch_no, v_offset))

    def channel_scale(instr,ch_no, v_scale):
        instr.write('CH%i:SCA %f' % (ch_no, v_scale))

    def horz_scale(instr,scale):
        instr.write('HOR:MODE:SCA %s' % scale)

    def bandwidth_full(instr,ch_no):
        instr.write('CH%i:BANDWIDTH FUL'%ch_no)

    def set_bandwidth(instr,ch_no,bw):
        instr.write('CH%i:BANDWIDTH %s'%(ch_no,bw))

    def autoset(instr):
        instr.write('AUTOS EXEC')

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

    ############## DPO JET functions (for jitter measurement) #############
    
    def dpojet_clr_meas(instr):
        instr.write('DPOJET:CLEARALLM')

    def dpojet_state(instr):
        return instr.query('DPOJET:STATE?')

    def dpojet_run(instr):
        instr.write('DPOJET:STATE RUN')

    def dpojet_stop(instr):
        instr.write('DPOJET:STATE STOP')

    def dpojet_population(instr,n):
        instr.write('DPOJET:POPULATION:LIMIT %i' %n)
        instr.write('DPOJET:POPULATION:STATE 1')

    def dpojet_period(instr):
        instr.write('DPOJET:ADDM PERI')

    def dpojet_result(instr):
        data = instr.query('DPOJET:MEAS1:RESUL:ALLA?').split(';;')
        return data

    def dpojet_status_query(instr):
        data = instr.query('DPOJET:MEAS1:RESUL:ALLA?').split(';;')
        curr_popu = int(data[0])
        return curr_popu

    def dpojet_quickset(instr,n):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        scope.dpojet_period(instr)
        scope.dpojet_population(instr,n)
        sleep(2)
        scope.dpojet_run(instr)
        sleep(2)
        status = scope.dpojet_status_query(instr)
        while status < n:
            sleep(10)
            status = scope.dpojet_status_query(instr)
        meas_val = scope.dpojet_result(instr)
        scope.dpojet_stop(instr)
        return meas_val


############ Custom functions #########################
    def delay(instr, ch1=1, ch2=2,edge_ch1 = 'RISE',edge_ch2 = 'FALL',direction ='FORW'): #use BACKW for reverse direction
        instr.write('MEASU:IMM:SOU1 CH%i' %ch1)
        instr.write('MEASU:IMM:SOU2 CH%i' %ch2)
        instr.write('MEASU:IMM:DEL:EDGE1 %s'%edge_ch1)
        instr.write('MEASU:IMM:DEL:EDGE2 %s'%edge_ch2)
        instr.write('MEASU:IMM:DEL:DIREC %s'%direction)
        instr.write('MEASU:IMM:TYP DEL')
        return float(instr.query('MEASU:IMM:VAL?'))

    def delay_imo(instr):
        instr.write('MEASU:IMM:SOU1 CH1')
        instr.write('MEASU:IMM:SOU2 CH2')
        instr.write('MEASU:IMM:DEL:EDGE1 RISE')
        instr.write('MEASU:IMM:DEL:EDGE2 FALL')
        instr.write('MEASU:IMM:DEL:DIREC FORW')
        instr.write('MEASU:IMM:TYP DEL')
        return float(instr.query('MEASU:IMM:VAL?'))

    def delay_ilo(instr):
        instr.write('MEASU:IMM:SOU1 CH1')
        instr.write('MEASU:IMM:SOU2 CH2')
        instr.write('MEASU:IMM:DEL:EDGE1 FALL')
        instr.write('MEASU:IMM:DEL:EDGE2 FALL')
        instr.write('MEASU:IMM:DEL:DIREC FORW')
        instr.write('MEASU:IMM:TYP DEL')
        return float(instr.query('MEASU:IMM:VAL?'))

    def delay_PDAC(instr):
        instr.write('MEASU:IMM:SOU1 CH1')
        instr.write('MEASU:IMM:SOU2 CH2')
        instr.write('MEASU:IMM:DEL:EDGE1 RISE')
        instr.write('MEASU:IMM:DEL:EDGE2 RISE')
        instr.write('MEASU:IMM:DEL:DIREC FORW')
        instr.write('MEASU:IMMED:REFL:PERC:MID2 95')
        instr.write('MEASU:IMM:TYP DEL')
        return float(instr.query('MEASU:IMM:VAL?'))

    def delay_NDAC_small(instr):
        instr.write('MEASU:IMM:SOU1 CH1')
        instr.write('MEASU:IMM:SOU2 CH2')
        instr.write('MEASU:IMM:DEL:EDGE1 RISE')
        instr.write('MEASU:IMM:DEL:EDGE2 FALL')
        instr.write('MEASU:IMM:DEL:DIREC BACKW')
        instr.write('MEASU:IMMED:REFL:PERC:MID2 30')
        instr.write('MEASU:IMM:TYP DEL')
        return float(instr.query('MEASU:IMM:VAL?'))

    def delay_NDAC(instr):
        instr.write('MEASU:IMM:SOU1 CH1')
        instr.write('MEASU:IMM:SOU2 CH2')
        instr.write('MEASU:IMM:DEL:EDGE1 RISE')
        instr.write('MEASU:IMM:DEL:EDGE2 FALL')
        instr.write('MEASU:IMM:DEL:DIREC BACKW')
        instr.write('MEASU:IMMED:REFL:PERC:MID2 10')
        instr.write('MEASU:IMM:TYP DEL')
        return float(instr.query('MEASU:IMM:VAL?'))

    def delay_UV(instr,Cur1_ypos1,cur2_ypos2):
        instr.write('CURS:STATE ON')
        instr.write('CURS:FUNC SCREEN')
        instr.write('CURS:SCREEN:STY LINE_X')
        instr.write('CURS:SOU1 CH1')
        instr.write('CURS:SOU2 CH2')
        instr.write('CURS:SCREEN:YPOSITION1 %f' %Cur1_ypos1)
        instr.write('CURS:SCREEN:YPOSITION2 %f' %cur2_ypos2)
        sleep(4)
        t1 = float(instr.query('CURS:SCREEN:XPOSITION1?'))
        t2 = float(instr.query('CURS:SCREEN:XPOSITION2?'))
        # print(t1)
        # print(t2)
        t3 = float(t2-t1)
        return t3

    def delay_UV_4(instr,threshold):
        instr.write('CURS:STATE ON')
        instr.write('CURS:FUNC WAVE')
        instr.write('CURS:SCREEN:STY LINE_X')
        instr.write('CURS:SOU1 CH1')
        instr.write('CURS:SOU2 CH2')
        instr.write('CURS:WAVE:POS2 0E-6')
        # instr.write('CURS:WAVE:POS1 -10E-6')
        y1 = 0
        h1 = -0.00002
        for i in range(50):
            h2 = float(h1 + 0.000001)
            # print(h2)
            # sleep(2)
            instr.write('CURS:WAVE:POS1 %f' % h2)
            sleep(5)
            y = (instr.query('CURS:WAVE:HPOS1?'))
            h = (instr.query('CURS:WAVE:POS1?'))
            # print(h)
            y1 = float(y[0:5])
            h1 = -float(h[1:5]) * (0.000001)
            # print(y1,h1)
            if y1 >= threshold:
                t = abs(h1 - 0)
                return t
                break

    def delay_UV_5(instr,threshold):
        instr.write('CURS:STATE ON')
        instr.write('CURS:FUNC WAVE')
        instr.write('CURS:SCREEN:STY LINE_X')
        instr.write('CURS:SOU1 CH1')
        instr.write('CURS:SOU2 CH2')
        instr.write('CURS:WAVE:POS2 0E-6')
        # instr.write('CURS:WAVE:POS1 -10E-6')
        y1 = 0
        h1 = -0.00002
        for i in range(50):
            h2 = float(h1 + 0.000001)
            # print(h2)
            # sleep(2)
            instr.write('CURS:WAVE:POS1 %f' % h2)
            sleep(5)
            y = (instr.query('CURS:WAVE:HPOS1?'))
            h = (instr.query('CURS:WAVE:POS1?'))
            # print(y,h)
            y1 = float(y[0:5])
            h1 = -float(h[1:5]) * (0.000001)
            # print(y1, h1)
            if y1 >= threshold:
                t = abs(h1 - (0))
                return t
                break

    def delay_gpio_lscsa_ac(instr):
        instr.write('MEASU:IMM:SOU1 CH2')
        instr.write('MEASU:IMM:SOU2 CH1')
        instr.write('MEASU:IMM:DEL:EDGE1 RISE')
        instr.write('MEASU:IMM:DEL:EDGE2 RISE')
        instr.write('MEASU:IMM:DEL:DIREC FORW')
        instr.write('MEASU:IMM:TYP DEL')
        return float(instr.query('MEASU:IMM:VAL?'))
        
    def delay_Tdelay_lscsa_ac(instr):
        instr.write('MEASU:IMM:SOU1 CH2')
        instr.write('MEASU:IMM:SOU2 CH3')
        instr.write('MEASU:IMM:DEL:EDGE1 RISE')
        instr.write('MEASU:IMM:DEL:EDGE2 RISE')
        instr.write('MEASU:IMM:DEL:DIREC FORW')
        instr.write('MEASU:IMM:TYP DEL')
        return float(instr.query('MEASU:IMM:VAL?'))


    def position(instr, ch_no, pos_val=0):
        instr.write('CH%i:POS %f' % (ch_no, pos_val))


    def disp_channel_on(instr, ch_no):
        instr.write('SELect:CH%i ON' % ch_no)


    def disp_channel_off(instr, ch_no):
        instr.write('SELect:CH%i OFF' % ch_no)


    def horz_sampling_rate(instr, rate=40e9):
        instr.write('HORizontal:MODE:MANual')
        # instr.write('HORizontal:MODE:CONStant')
        instr.write('HORizontal:MODE:SAMPLERate %i' % rate)


    def record_length(instr, length=0.1e6):
        instr.write('HORizontal:MODE:MANual')
        instr.write('HORizontal:MODE:RECOrdlength %i' % length)


    def horizontal_position(instr, pos_val_perc=14):
        instr.write('HORizontal:POSition %f' % (pos_val_perc))


    def hi_res_mode(instr):
        instr.write('ACQ:MOD HIRes')
        print(instr.query('ACQ:MOD:ACTU?'))


    def cursor_gating(instr, ch_sel=1, start_pos=0, end_pos=1.08e-6):
        instr.write('CURSOR:SOURCE 1 CH%i' % ch_sel)
        instr.write('CURSOR:SOURCE 2 CH%i' % ch_sel)
        instr.write('CURSOR:VBARS:POSITION1 %s' % start_pos)
        instr.write('CURSOR:VBARS:POSITION2 %s' % end_pos)


    def scope_default_usb(ch_sel=1):
        scope.clear_all(dso)
        disp_channel_off(dso, ch_no=1)
        disp_channel_off(dso, ch_no=3)
        disp_channel_off(dso, ch_no=2)
        disp_channel_off(dso, ch_no=4)
        disp_channel_on(dso, ch_no=ch_sel)
        cursor_gating(dso, ch_sel=ch_sel)
        horz_sampling_rate(dso, rate=10e9)
        record_length(dso, length=20e3)
        horizontal_position(dso, pos_val_perc=10)
        # scope.horz_scale(dso, 200e-9)
        scope.channel_offset(dso, ch_no=ch_sel, v_offset=0)
        position(dso, ch_no=ch_sel, pos_val=0)
        # hi_res_mode(dso)
        scope.set_bandwidth(dso, ch_no=ch_sel, bw=1500e6)
        scope.channel_scale(dso, ch_no=ch_sel, v_scale=0.1)
        scope.trigger_quickset_rise(dso, ch_no=ch_sel, lev=0)


    def scope_default_usb_sma(ch_sel_dp=1, ch_sel_dm=2):
        scope.clear_all(dso)
        disp_channel_off(dso, ch_no=1)
        disp_channel_off(dso, ch_no=3)
        disp_channel_off(dso, ch_no=2)
        disp_channel_off(dso, ch_no=4)
        disp_channel_on(dso, ch_no=ch_sel_dp)
        disp_channel_on(dso, ch_no=ch_sel_dm)
        cursor_gating(dso, ch_sel=ch_sel_dp)
        horz_sampling_rate(dso, rate=40e9)
        record_length(dso, length=100e3)
        horizontal_position(dso, pos_val_perc=10)
        # scope.horz_scale(dso, 200e-9)
        scope.channel_offset(dso, ch_no=ch_sel_dp, v_offset=0)
        scope.channel_offset(dso, ch_no=ch_sel_dm, v_offset=0)
        position(dso, ch_no=ch_sel_dp, pos_val=0)
        position(dso, ch_no=ch_sel_dm, pos_val=0)
        # hi_res_mode(dso)
        scope.set_bandwidth(dso, ch_no=ch_sel_dp, bw=2500e6)
        scope.set_bandwidth(dso, ch_no=ch_sel_dm, bw=2500e6)
        scope.channel_scale(dso, ch_no=ch_sel_dp, v_scale=0.1)
        scope.channel_scale(dso, ch_no=ch_sel_dm, v_scale=0.1)
        scope.trigger_quickset_rise(dso, ch_no=ch_sel_dp, lev=0)
        dso.write('SELect:MATH1 ON')
        dso.write('MATH1:DEFINE "CH%i-CH%i"' % (ch_sel_dp, ch_sel_dm))


    def scope_default_eusb_sma(ch_sel_dp=3, ch_sel_dm=4):
        scope.clear_all(dso)
        disp_channel_off(dso, ch_no=1)
        disp_channel_off(dso, ch_no=3)
        disp_channel_off(dso, ch_no=2)
        disp_channel_off(dso, ch_no=4)
        disp_channel_on(dso, ch_no=ch_sel_dp)
        disp_channel_on(dso, ch_no=ch_sel_dm)
        cursor_gating(dso, ch_sel=ch_sel_dp)
        horz_sampling_rate(dso, rate=40e9)
        record_length(dso, length=100e3)
        horizontal_position(dso, pos_val_perc=10)
        # scope.horz_scale(dso, 200e-9)
        scope.channel_offset(dso, ch_no=ch_sel_dp, v_offset=0)
        scope.channel_offset(dso, ch_no=ch_sel_dm, v_offset=0)
        position(dso, ch_no=ch_sel_dp, pos_val=0)
        position(dso, ch_no=ch_sel_dm, pos_val=0)
        # hi_res_mode(dso)
        scope.set_bandwidth(dso, ch_no=ch_sel_dp, bw=2500e6)
        scope.set_bandwidth(dso, ch_no=ch_sel_dm, bw=2500e6)
        scope.channel_scale(dso, ch_no=ch_sel_dp, v_scale=0.06)
        scope.channel_scale(dso, ch_no=ch_sel_dm, v_scale=0.06)
        scope.trigger_quickset_rise(dso, ch_no=ch_sel_dp, lev=0)
        dso.write('SELect:MATH2 ON')
        dso.write('MATH2:DEFINE "CH%i-CH%i"' % (ch_sel_dp, ch_sel_dm))


    def scope_default_eusb(ch_sel=1):
        scope.clear_all(dso)
        # print(dso.write('CH2:TERmination 1000000'))
        disp_channel_off(dso, ch_no=1)
        disp_channel_off(dso, ch_no=2)
        disp_channel_off(dso, ch_no=3)
        disp_channel_off(dso, ch_no=4)
        disp_channel_on(dso, ch_no=ch_sel)
        cursor_gating(dso, ch_sel=ch_sel)
        # horz_sampling_rate(dso,rate=4e12)
        # horz_sampling_rate(dso,rate=2.5e9)
        horz_sampling_rate(dso, rate=10e9)
        # record_length(dso, length=5e3)
        record_length(dso, length=20e3)
        horizontal_position(dso, pos_val_perc=10)
        scope.horz_scale(dso, 200e-9)
        scope.channel_offset(dso, ch_no=ch_sel, v_offset=0)
        position(dso, ch_no=ch_sel, pos_val=0)
        # hi_res_mode(dso)
        scope.set_bandwidth(dso, ch_no=ch_sel, bw=1500e6)
        scope.channel_scale(dso, ch_no=ch_sel, v_scale=0.06)
        scope.trigger_quickset_rise(dso, ch_no=1, lev=0)


    def save_waveform_csv(instr, ch_no='CH1', file_name='test1', start_point=0, end_point=50e3):
        # des_path = r'C:\Users\Tek_Local_Admin\Tektronix\TekScope\Waveforms\automated_'+ file_name +'.csv'
        # instr.write('SAVe:WAVEform:FORCESAMEFilesize')
        instr.write('SAVe:WAVEform:FILEFormat SPREADSHEETCsv')
        instr.write('SAVe:WAVEform:DATa:STARt %i' % start_point)
        instr.write('SAVe:WAVEform:DATa:STOP %i' % end_point)
        instr.write('SAVe:WAVEFORM %s,"%s.csv"' % (ch_no, file_name))


    def save_waveform_wfm(instr, ch_no='CH1', file_name='test1'):
        # des_path = r'C:\Users\Tek_Local_Admin\Tektronix\TekScope\Waveforms\automated_'+ file_name +'.csv'
        # instr.write('SAVe:WAVEform:FORCESAMEFilesize')
        # instr.write('SAVe:WAVEform:DATa:STARt %i' %start_point)
        # instr.write('SAVe:WAVEform:DATa:STOP %i' %end_point)
        instr.write('SAVe:WAVEform:FILEFormat INTERNal')
        instr.write('SAVe:WAVEFORM %s,"%s.wfm"' % (ch_no, file_name))


    def pulse_width_trigger(instr, ch_no=1, lev=0, min_pul_width=16e-9, max_pul_width=20e-9, polarity='POSITIVe'):
        # instr.write('TRIG:A:EDGE:SOU CH%i' % ch_no)
        instr.write('TRIGger:A:PULse:WIDth:LOWLimit %s' % (min_pul_width))
        instr.write('TRIGger:A:PULse:WIDth:HIGHLimit %s' % (max_pul_width))
        instr.write('TRIGGER:A:PULSE:SOURCE CH%i' % ch_no)
        instr.write('TRIGger:A:PULse:WIDth:POLarity:CH%i %s' % (ch_no, polarity))
        instr.write('TRIGger:A:PULse:WIDth:QUAlify OCCurs')
        instr.write('TRIG:A:LEV:CH%i %f' % (ch_no, lev))


    ###########dpojet_advanced functions#####################
    def source_autoset(instr, measurement_source1='CH1'):
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write("DPOJET:SOURCEAutoset BOTH")  # {HORIzontal | VERTical}
        # instr.write('DPOJET:MEAS1:SOUrce2 %s' % measurement_source2)


    def reference_level_rise_percent(instr, measurement_source='CH1', rise_high=90, rise_low=10,
                                     rise_mid=50):
        # instr.write("DPOJET:REFLevels:%s:PERcent" %measurement_source)
        instr.write("DPOJET:REFLevels:%s:PERcent:RISEHigh %f" % (measurement_source, rise_high))
        instr.write("DPOJET:REFLevels:%s:PERcent:RISELow %f" % (measurement_source, rise_low))
        instr.write("DPOJET:REFLevels:%s:PERcent:RISEMid %f" % (measurement_source, rise_mid))


    def reference_level_fall_percent(instr, measurement_source='CH1', fall_high=90, fall_low=10,
                                     fall_mid=50):
        # instr.write("DPOJET:REFLevels:%s:PERcent" % measurement_source)
        instr.write("DPOJET:REFLevels:%s:PERcent:FALLHigh %f" % (measurement_source, fall_high))
        instr.write("DPOJET:REFLevels:%s:PERcent:FALLLow %f" % (measurement_source, fall_low))
        instr.write("DPOJET:REFLevels:%s:PERcent:FALLMid %f" % (measurement_source, fall_mid))


    def reference_level_rise_absolute(instr, measurement_source='CH1', rise_high=1, rise_low=-1,
                                      rise_mid=0):
        instr.write('DPOJET:REFLevels:%s:AUTOSet 0' % measurement_source)
        instr.write("DPOJET:REFLevels:%s:ABsolute" % measurement_source)
        instr.write("DPOJET:REFLevels:%s:ABsolute:RISEHigh %f" % (measurement_source, rise_high))
        instr.write("DPOJET:REFLevels:%s:ABsolute:RISELow %f" % (measurement_source, rise_low))
        instr.write("DPOJET:REFLevels:%s:ABsolute:RISEMid %f" % (measurement_source, rise_mid))


    def reference_level_fall_absolute(instr, measurement_source='CH1', fall_high=1, fall_low=-1,
                                      fall_mid=0):
        instr.write('DPOJET:REFLevels:%s:AUTOSet 0' % measurement_source)
        instr.write("DPOJET:REFLevels:%s:ABsolute" % measurement_source)
        instr.write("DPOJET:REFLevels:%s:ABsolute:FALLHigh %f" % (measurement_source, fall_high))
        instr.write("DPOJET:REFLevels:%s:ABsolute:FALLLow %f" % (measurement_source, fall_low))
        instr.write("DPOJET:REFLevels:%s:ABsolute:FALLMid %f" % (measurement_source, fall_mid))


    def reference_level_hys_absolute(instr, measurement_source='CH1', hys=0.03):
        # instr.write("DPOJET:REFLevels:%s:ABsolute" % measurement_source)
        instr.write("DPOJET:REFLevels:%s:ABsolute:HYSTeresis %f" % (measurement_source, hys))


    def dpojet_rise_fall_time_meas_config(instr, measurement_source1='CH1'):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        sleep(2)
        instr.write('DPOJET:ADDM FALLtime')
        instr.write('DPOJET:ADDM RISEtime')
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS2:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:GATING CURSOR')


    def dpojet_rise_fall_time_meas_recalculate(instr):
        dso.write("DPOJET:STATE CLEAR")
        sleep(1)
        dso.write("DPOJET:STATE RECALC")
        sleep(10)
        try:
            meas_mean_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:MEAN?'))
            meas_std_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:STDDev?'))
            meas_min_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:MIN?'))
            meas_max_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:MAX?'))
            meas_pop_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:POPUlation?'))
            meas_mean_r = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MEAN?'))
            meas_std_r = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:STDDev?'))
            meas_min_r = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MIN?'))
            meas_max_r = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MAX?'))
            meas_pop_r = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:POPUlation?'))

            meas_val = [meas_mean_f, meas_std_f, meas_max_f, meas_min_f, meas_pop_f, meas_mean_r, meas_std_r, meas_max_r,
                        meas_min_r, meas_pop_r]
        except:
            meas_val = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
        return meas_val


    def dpojet_maskhit_config_v0(instr, measurement_source1='CH1',
                                 mask_filename='USB2_Mask_Near_End', clear_previous_plots=1):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        sleep(1)
        instr.write('DPOJET:ADDM MASKHits')
        # instr.write('DPOJET:ADDM FALLtime')
        # instr.write('DPOJET:ADDM RISEtime')
        # instr.write('DPOJET:ADDM HIGHTime')
        # instr.write('DPOJET:ADDM LOWTime')
        # instr.write('DPOJET:ADDM SKEW')
        # instr.write('DPOJET:ADDM RISESLEWrate')
        # instr.write('DPOJET:ADDM FALLSLEWrate')
        instr.write('DPOJET:ADDM WIDth')
        instr.write('DPOJET:ADDM HEIght')
        instr.write('DPOJET:ADDM HIGHLOW')
        # instr.write('DPOJET:ADDM DJ')
        # instr.write('DPOJET:ADDM RJ')
        # instr.write('DPOJET:ADDM VDIFFxovr')
        ############
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS2:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS3:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS4:SOUrce1 %s' % measurement_source1)
        # instr.write('DPOJET:MEAS5:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS6:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS7:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS8:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS9:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS10:SOUrce1 %s' %measurement_source1)
        if clear_previous_plots == 1:
            instr.write('DPOJET:CLEARALLPlots')

        print('old mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        instr.write('DPOJET:MEAS1:MASKfile ' + '\"' +
                    r'C:\Users\Public\Tektronix\TekApplications\DPOJET\Masks\%s' % mask_filename
                    + '.msk' + '\"')
        print('updated mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        # instr.write('DPOJET:ADDP EYE MEAS1')
        # print('old mask file = ',instr.query('DPOJET:PLOT1:EYE:MASKfile?'))
        # instr.write('DPOJET:PLOT1:EYE:MASKfile ' + '\"' +
        #                   r'C:\Users\Public\Tektronix\TekApplications\DPOJET\Masks\%s' %mask_filename
        #                   + '.msk' + '\"')
        # print('updated mask file = ',instr.query('DPOJET:PLOT1:EYE:MASKfile?'))
        sleep(5)


    def dpojet_maskhit_config(instr, measurement_source1='CH1',
                              mask_filename='USB2_Mask_Near_End', clear_previous_plots=1):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        sleep(1)
        instr.write('DPOJET:ADDM MASKHits')
        # instr.write('DPOJET:ADDM FALLtime')
        # instr.write('DPOJET:ADDM RISEtime')
        # instr.write('DPOJET:ADDM HIGHTime')
        # instr.write('DPOJET:ADDM LOWTime')
        # instr.write('DPOJET:ADDM SKEW')
        # instr.write('DPOJET:ADDM RISESLEWrate')
        # instr.write('DPOJET:ADDM FALLSLEWrate')
        # instr.write('DPOJET:ADDM WIDth')
        # instr.write('DPOJET:ADDM HEIght')
        instr.write('DPOJET:ADDM HIGHLOW')
        instr.write('DPOJET:ADDM CYCLEPktopk')

        # instr.write('DPOJET:ADDM VDIFFxovr')
        ############
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS2:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS3:SOUrce1 %s' % measurement_source1)
        # instr.write('DPOJET:MEAS4:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS5:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS6:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS7:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS8:SOUrce1 %s' %measurement_source1)
        # instr.write('DPOJET:MEAS9:SOUrce1 %s' %measurement_source1)
        instr.write('DPOJET:GATING CURSOR')
        if clear_previous_plots == 1:
            instr.write('DPOJET:CLEARALLPlots')

        print('old mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        instr.write('DPOJET:MEAS1:MASKfile ' + '\"' +
                    r'C:\Users\Public\Tektronix\TekApplications\DPOJET\Masks\%s' % mask_filename
                    + '.msk' + '\"')
        print('updated mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        # instr.write('DPOJET:ADDP EYE MEAS1')
        # print('old mask file = ',instr.query('DPOJET:PLOT1:EYE:MASKfile?'))
        # instr.write('DPOJET:PLOT1:EYE:MASKfile ' + '\"' +
        #                   r'C:\Users\Public\Tektronix\TekApplications\DPOJET\Masks\%s' %mask_filename
        #                   + '.msk' + '\"')
        # print('updated mask file = ',instr.query('DPOJET:PLOT1:EYE:MASKfile?'))
        sleep(5)


    def dpojet_maskhit_acquisition(instr):
        instr.write("DPOJET:STATE CLEAR")
        sleep(1)
        instr.write("DPOJET:STATE RECALC")
        sleep(5)
        try:
            meas_mean_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MEAN?'))
            meas_std_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:STDDev?'))
            meas_min_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MIN?'))
            meas_max_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MAX?'))
            meas_pop_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:POPUlation?'))
            meas_mean_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MEAN?'))
            meas_std_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:STDDev?'))
            meas_min_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MIN?'))
            meas_max_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MAX?'))
            meas_pop_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:POPUlation?'))

            meas_val = [meas_mean_f, meas_std_f, meas_max_f, meas_min_f, meas_pop_f, meas_mean_r, meas_std_r,
                        meas_max_r, meas_min_r, meas_pop_r]
        except:
            meas_val = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
        return meas_val


    def dpojet_report_save(instr, report_name='test_report1'):
        instr.write("DPOJET:REPORT:AUTOincrement 0")
        instr.write("DPOJET:REPORT:APPlicationconfig 1")
        # updating report name
        report_path = r'C:\Users\Tek_Local_Admin\Tektronix\TekApplications\DPOJET\Reports\automated_' + report_name + '.mht'
        print(report_path)
        instr.write('DPOJET:REPORT:REPORTName ' + '\"' + report_path + '\"')
        curr_report_name = instr.query("DPOJET:REPORT:REPORTName?")
        instr.write("DPOJET:REPORT EXECute")  # APPEnd
        sleep(5)
        print(instr.query("DPOJET:REPORT:STATE?"))
        instr.write("DPOJET:REPORT:VIEWreport 1")
        return curr_report_name


    def dpojet_plot_save(instr, plot_name='test_plot_1'):
        instr.write('DPOJET:EXPORT PLOT1, "%s.png"' % plot_name)


    def dpojet_high_meas(instr, measurement_source1='CH1'):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        sleep(1)
        instr.write('DPOJET:ADDM HIGH')
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:GATING CURSOR')
        instr.write("DPOJET:STATE CLEAR")
        sleep(1)
        instr.write("DPOJET:STATE RECALC")
        sleep(5)
        try:
            meas_mean = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:MEAN?'))
        except:
            print('Could not find high level, hence setting it to zero')
            meas_mean = 0
        return meas_mean


    def dpojet_pree_config(instr, measurement_source1='CH1',
                           mask_filename='USB2_Mask_Near_End', clear_previous_plots=1, ref_overshoot=0,
                           ref_time_over_level=0):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        sleep(1)
        instr.write('DPOJET:ADDM MASKHits')
        instr.write('DPOJET:ADDM HIGH')
        # instr.write('DPOJET:ADDM TIMEOUTSIDELEVEL')
        instr.write('DPOJET:ADDM OVERShoot')
        ############
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS2:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS3:SOUrce1 %s' % measurement_source1)
        #############
        instr.write('DPOJET:GATING CURSOR')
        instr.write('DPOJET:MEAS3:REFVoltage %f' % ref_overshoot)
        print(instr.query('DPOJET:MEAS3:REFVoltage?'))

        if clear_previous_plots == 1:
            instr.write('DPOJET:CLEARALLPlots')

        print('old mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        instr.write('DPOJET:MEAS1:MASKfile ' + '\"' +
                    r'C:\Users\Public\Tektronix\TekApplications\DPOJET\Masks\%s' % mask_filename
                    + '.msk' + '\"')
        print('updated mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        sleep(5)


    def dpojet_pree_acquisition(instr):
        instr.write("DPOJET:STATE CLEAR")
        sleep(1)
        instr.write("DPOJET:STATE RECALC")
        sleep(10)
        try:
            meas_mean_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MEAN?'))
            meas_std_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:STDDev?'))
            meas_min_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MIN?'))
            meas_max_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MAX?'))
            meas_pop_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:POPUlation?'))
            meas_mean_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MEAN?'))
            meas_std_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:STDDev?'))
            meas_min_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MIN?'))
            meas_max_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MAX?'))
            meas_pop_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:POPUlation?'))

            meas_val = [meas_mean_f, meas_std_f, meas_max_f, meas_min_f, meas_pop_f, meas_mean_r, meas_std_r,
                        meas_max_r, meas_min_r, meas_pop_r]
        except:
            meas_val = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
        return meas_val


    def dpojet_slew_config(instr, measurement_source1='CH1',
                           mask_filename='USB2_Mask_Near_End', clear_previous_plots=1):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        sleep(1)
        instr.write('DPOJET:ADDM MASKHits')
        instr.write('DPOJET:ADDM RISESLEWrate')
        instr.write('DPOJET:ADDM FALLSLEWrate')
        ############
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS2:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS3:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:GATING CURSOR')
        if clear_previous_plots == 1:
            instr.write('DPOJET:CLEARALLPlots')
        print('old mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        instr.write('DPOJET:MEAS1:MASKfile ' + '\"' +
                    r'C:\Users\Public\Tektronix\TekApplications\DPOJET\Masks\%s' % mask_filename
                    + '.msk' + '\"')
        print('updated mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        sleep(5)


    def dpojet_slew_acquisition(instr):
        instr.write("DPOJET:STATE CLEAR")
        sleep(2)
        instr.write("DPOJET:STATE RECALC")
        sleep(5)
        try:
            meas_mean_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MEAN?'))
            meas_std_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:STDDev?'))
            meas_min_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MIN?'))
            meas_max_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:MAX?'))
            meas_pop_f = float(instr.query('DPOJET:MEAS2:RESULts:ALLAcqs:POPUlation?'))
            meas_mean_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MEAN?'))
            meas_std_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:STDDev?'))
            meas_min_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MIN?'))
            meas_max_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:MAX?'))
            meas_pop_r = float(instr.query('DPOJET:MEAS3:RESULts:ALLAcqs:POPUlation?'))

            meas_val = [meas_mean_f, meas_std_f, meas_max_f, meas_min_f, meas_pop_f, meas_mean_r, meas_std_r,
                        meas_max_r, meas_min_r, meas_pop_r]
        except:
            meas_val = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
        return meas_val


    def dpojet_dc_common_mode_config(instr, measurement_source1='CH1', measurement_source2='CH2'):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        sleep(1)
        instr.write('DPOJET:ADDM Commonmode')
        ############
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS2:SOUrce2 %s' % measurement_source2)
        instr.write('DPOJET:GATING CURSOR')


    def dpojet_dc_common_mode_cal(instr, duration=5):
        instr.write("DPOJET:STATE CLEAR")
        sleep(2)
        instr.write("DPOJET:STATE RUN")
        sleep(duration)
        scope.dpojet_stop(instr)
        try:
            meas_mean_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:MEAN?'))
            meas_std_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:STDDev?'))
            meas_min_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:MIN?'))
            meas_max_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:MAX?'))
            meas_pop_f = float(instr.query('DPOJET:MEAS1:RESULts:ALLAcqs:POPUlation?'))
            meas_val = [meas_mean_f, meas_std_f, meas_max_f, meas_min_f, meas_pop_f]
        except:
            meas_val = ['NA', 'NA', 'NA', 'NA', 'NA']

        return meas_val


    def dpojet_maskhit_config_noise(instr, measurement_source1='CH1',
                                    mask_filename='USB2_Mask_Near_End', clear_previous_plots=1):
        scope.dpojet_stop(instr)
        scope.dpojet_clr_meas(instr)
        sleep(1)
        instr.write('DPOJET:ADDM MASKHits')
        instr.write('DPOJET:ADDM TIE')
        instr.write('DPOJET:MEAS1:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:MEAS2:SOUrce1 %s' % measurement_source1)
        instr.write('DPOJET:GATING CURSOR')
        if clear_previous_plots == 1:
            instr.write('DPOJET:CLEARALLPlots')
        print('old mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        instr.write('DPOJET:MEAS1:MASKfile ' + '\"' +
                    r'C:\Users\Public\Tektronix\TekApplications\DPOJET\Masks\%s' % mask_filename
                    + '.msk' + '\"')
        print('updated mask file = ', instr.query('DPOJET:MEAS1:MASKfile?'))
        sleep(5)


