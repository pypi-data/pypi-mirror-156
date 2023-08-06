from auto_instr import *
from time import sleep

class tempforce_t2500(object):

    def airoff(instr):
        instr.write('AIROFF')

    def head_down(instr):
        instr.write('HEAD 0\n')

    def head_up(instr):
        instr.write('HEAD 1\n')

    def max_temp(instr, temp = 150):
        instr.write('MAXTEMP '+ str(temp))
        return instr.query('MAXTEMP?')

    def min_temp(instr, temp = -70):
        instr.write('MINTEMP '+ str(temp))
        return instr.query('MINTEMP?')

    def temp_tolerance(instr, temp_tol = 2):
        instr.write('TEMPTOL '+ str(temp_tol))
        return instr.query('TEMPTOL?')

    def meas_air_temp(instr):
        return float(instr.query('AIRTEMP?').split(' ')[0])

    def meas_DUT_temp(instr):
        return  float(instr.query('DUTTEMP?').split(' ')[0])

    def dut_sensor_type(instr,type = 0): #1 for K type(Yellow), 2 for T type (Blue), 3 for RTD
        instr.write('TCONTROL '+ str(type))
        instr.write('TDISPLAY '+ str(type))

    def set_temp_air(instr, temp=25, soak=150):
        current = float(instr.query('AIRTEMP?').split(' ')[0])
        instr.write('TEMP1 ' + str(temp))
        if temp < 25:
            instr.write('COMP 1')
        instr.write('GOTEMP1')
        while (abs(current - temp) > 1):
            current = float(instr.query('AIRTEMP?').split(' ')[0])
            sleep(soak)

    def set_temp_dut(instr, temp=25, soak=150):
        current = float(instr.query('DUTTEMP?').split(' ')[0])
        instr.write('TEMP1 ' + str(temp))
        if temp < 25:
            instr.write('COMP 1')
        instr.write('GOTEMP1')
        while (abs(current - temp) > 1):
            current = float(instr.query('DUTTEMP?').split(' ')[0])
            sleep(soak)

    def quick_set(instr, temp =25, soak =120 ,type =0):#1 for K type(Yellow), 2 for T type (Blue), 3 for RTD
        tempforce_t2500.dut_sensor_type(instr,type)
        tempforce_t2500.head_down(instr)
        if type !=0:
            tempforce_t2500.set_temp_dut(instr,temp,soak)
        else:
            tempforce_t2500.set_temp_air(instr, temp, soak)
