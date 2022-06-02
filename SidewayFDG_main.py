# SiDG script (using Omega USB pressure transducer)
# written by Jheng-Han Tsai, September 2020
##############################################################################
import threading
import time
import pandas as pd
import numpy as np
from scipy import signal, interpolate, stats
import concurrent.futures
import os

#from zaberbinary import BinarySerial, BinaryDevice, BinaryCommand, BinaryReply
#import nidaqmx
#from nidaqmx.constants import TerminalConfiguration, VoltageUnits, Edge, AcquisitionType 
#import harvard

import tkinter as tk
from tkinter import ttk
import matplotlib 
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
#import PX409USBH

########### Interface #########################################
style.use('seaborn-whitegrid')

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

def animate(i):    
    ani_name = folder_data + 'tempDataForAnimation.csv'
    pullData = pd.read_csv(ani_name)
    x_E = pullData['E_operation time']
    y_E = pullData['E_thickness']
    x_S = pullData['S_operation time']
    y_S = pullData['S_thickness']

    a.clear()
    a.plot(x_E, y_E, 'bs', x_S, y_S, 'r^')
    a.set_xlabel('Time (s)')
    a.set_ylabel('Thickness (mm)')



# Tkinter code starts
window = tk.Tk()
window.title('SiDG GUI')
window.geometry('900x680')


# Create Tab Control
tabControl = ttk.Notebook(window)          
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='Main')
tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text='Detailed information')
tabControl.pack(expand=1, fill="both")




# Figure
canvas = FigureCanvasTkAgg(f, tab1)
canvas.draw()
canvas.get_tk_widget().place(x = 300, y = 300)
canvas._tkcanvas.place(x = 380, y = 30)

# Labels and Entrys
l1 = tk.Label(tab1, text = 'X-axis Positioner - ', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 20)
l2 = tk.Label(tab1, text = 'Distance to move (mm)("-" moves forward):', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 40)
e1_var = tk.StringVar(value = '0')
e1 = tk.Entry(tab1, textvariable = e1_var)
e1.place(x = 10, y = 65)

l3 = tk.Label(tab1, text = 'Z-axis Positioner - ', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 120)
l4 = tk.Label(tab1, text = 'Distance to move (mm)("-" moves down):', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 140)
e2_var = tk.StringVar(value = '0')
e2 = tk.Entry(tab1, textvariable = e2_var)
e2.place(x = 10, y = 165)

l5 = tk.Label(tab1, text = 'SiDG Controller - ', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 240)
l6 = tk.Label(tab1, text = 'Select a folder for steps:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 260)
e3_var = tk.StringVar(value = 'steps/')
e3 = tk.Entry(tab1, textvariable = e3_var)
e3.place(x = 10, y = 280)

l7 = tk.Label(tab1, text = 'Select a folder for saving data:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 300)
e4_var = tk.StringVar(value = 'data/')
e4 = tk.Entry(tab1, textvariable = e4_var)
e4.place(x = 10, y = 320)

l8 = tk.Label(tab1, text = 'Calibration mode ---------------------------------------------\
              ', width = 50, height = 2, anchor = 'nw').place(x = 10, y = 340)
l9 = tk.Label(tab1, text = 'Select a file for calibration steps:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 360)
e5_var = tk.StringVar(value = 'X.csv')
e5 = tk.Entry(tab1, textvariable = e5_var)
e5.place(x = 10, y = 380)

#l10_var = 0
#l10_text = 'Note: Theoritical offset: ' + str(l10_var) + ' mm.'
#l10 = tk.Label(tab1, text = l10_text, width = 25, height = 2, anchor = 'nw').place(x = 160, y = 405)


l11 = tk.Label(tab1, text = 'Measurement mode ------------------------------------------\
               ', width = 50, height = 2, anchor = 'nw').place(x = 10, y = 420)
l12 = tk.Label(tab1, text = 'Select a file for Z-axis steps:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 440)
e6_var = tk.StringVar(value = 'Z.csv')
e6 = tk.Entry(tab1, textvariable = e6_var)
e6.place(x = 10, y = 460)

l13 = tk.Label(tab1, text = 'Select a file for Cd reference:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 480)
e7_var = tk.StringVar(value = 'cal.csv')
e7 = tk.Entry(tab1, textvariable = e7_var)
e7.place(x = 10, y = 500)

l14 = tk.Label(tab1, text = 'Enter the length of X-axis positioner (mm):', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 520)
e8_var = tk.StringVar(value = '6')
e8 = tk.Entry(tab1, textvariable = e8_var)
e8.place(x = 10, y = 540)

l15 = tk.Label(tab1, text = 'Enter the offset (mm):', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 560)
e9_var = tk.StringVar(value = '0')
e9 = tk.Entry(tab1, textvariable = e9_var)
e9.place(x = 10, y = 580)

l16 = tk.Label(tab1, text = 'Enter the maximum pressure tolerance (Pa):', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 600)
e10_var = tk.StringVar(value = '10000')
e10 = tk.Entry(tab1, textvariable = e10_var)
e10.place(x = 10, y = 620)

l17 = tk.Label(tab1, text = 'Swelling profile. Colour: blue - Ejection; red - Suction', width = 40, height = 2, anchor = 'nw').place(x = 500, y = 530)

# tab2 labels and entrys
ll1 = tk.Label(tab2, text = 'Parameters for calculating discharge coefficient ------------------------------------------\
               ', width = 50, height = 2, anchor = 'nw').place(x = 10, y = 20)
ll2 = tk.Label(tab2, text = 'Density (kg/m3):', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 40)
ee1_var = tk.StringVar(value = '997.3')
ee1 = tk.Entry(tab2, textvariable = ee1_var)
ee1.place(x = 10, y = 60)

ll3 = tk.Label(tab2, text = 'Start point to be filtered for data collected from DAQ (s):', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 80)
ee2_var = tk.StringVar(value = '4')
ee2 = tk.Entry(tab2, textvariable = ee2_var)
ee2.place(x = 10, y = 100)

ll4 = tk.Label(tab2, text = 'Diameter of syringe (mm):', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 120)
ee3_var = tk.StringVar(value = '23')
ee3 = tk.Entry(tab2, textvariable = ee3_var)
ee3.place(x = 10, y = 140)


ll10 = tk.Label(tab2, text = 'Equipment ports ------------------------------------------\
               ', width = 50, height = 2, anchor = 'nw').place(x = 10, y = 220)
ll10 = tk.Label(tab2, text = 'X-axis positioner:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 240)
ee10_var = tk.StringVar(value = 'COM4')
ee10 = tk.Entry(tab2, textvariable = ee10_var)
ee10.place(x = 10, y = 260)

ll11 = tk.Label(tab2, text = 'Z-axis positioner:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 280)
ee11_var = tk.StringVar(value = 'COM5')
ee11 = tk.Entry(tab2, textvariable = ee11_var)
ee11.place(x = 10, y = 300)

ll12 = tk.Label(tab2, text = 'Syringe pump:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 320)
ee12_var = tk.StringVar(value = 'COM6')
ee12 = tk.Entry(tab2, textvariable = ee12_var)
ee12.place(x = 10, y = 340)

ll13 = tk.Label(tab2, text = 'Pressure transducer:', width = 40, height = 2, anchor = 'nw').place(x = 10, y = 360)
ee13_var = tk.StringVar(value = 'COM12')
ee13 = tk.Entry(tab2, textvariable = ee13_var)
ee13.place(x = 10, y = 380)

#################### Collect parameters firstly ##############################
folder_steps = e3.get()
folder_data = e4.get()

rho = ee1.get()
filteredPoint = ee2.get()
diameter_syringe = ee3.get()

COM4 = ee10.get()
COM5 = ee11.get()
COM6 = ee12.get()
COM12 = ee13.get()

#################### Zaber T-serial Positioner ###############################
class Zaber():
    def __init__(self):
        # Open a serial port.
        self.portZ = BinarySerial(COM5)
        self.portX = BinarySerial(COM4)
        # Get a handle for device #1 on the serial chain. This assumes you have a
        # device already in ASCII 115,220 baud mode at address 1 on your port.
        self.deviceZ = BinaryDevice(self.portZ, 1) # Device number 2
        self.deviceX = BinaryDevice(self.portX, 2) # Device number 1       
        print('Opening Zaber.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
	#This is the class destructor, ensures that the stage is not left active on exit
        try:
            self.portZ.close()
            self.portX.close()
        except:
            pass
        print('Closing Zaber.')
    
    def moveDown(self, steps):
        # Now move the device to a non-home position.
        print ('Z-axis zaber moves '+'{:.2f}'.format(steps/2000)+' mm ('+str(int(steps))+' steps). \n')
        reply = self.deviceZ.move_rel(steps) # move rel 2000 microsteps
    
    def moveLeft(self, steps):
        # Now move the device to a non-home position.
        print ('X-axis zaber moves '+'{:.2f}'.format(steps/2000)+' mm ('+str(int(steps))+' steps). \n')
        reply = self.deviceX.move_rel(steps) # move rel 2000 microsteps
    
    def upToHome(self):
        # Home the device and check the result.
        print ('Z-axis zaber goes home.\n')
        reply = self.deviceZ.home()
    
    def rightToHome(self):
        # Home the device and check the result.
        print ('X-axis zaber goes home.\n')
        reply = self.deviceX.home()

    def calibration(self, stepsX_path):
        stepsX_cal = np.array(pd.read_csv(stepsX_path))
        print (stepsX_cal)
        df = pd.DataFrame({'X' : [],
                    'Z' : [],
                    'direction' : [],
                    'flowrate' : [],
                    'targettime' : [],
                    'pressure mean': [],
                    'pressure std': [],
                    'Cd mean': [],
                    'Cd std': [],
                    'Cd se': [],
                    'Cd n': []})
        
        loop = stepsX_cal.shape[0]
        for i in range(0,loop):
            print (i)
            ###### Z-axis Zaber positioner ######
            if i == 0:
                stepsZ = 0
            else:
                movestepsZ = -(stepsX_cal[i,1]-stepsX_cal[i-1,1])
                if movestepsZ == 0:
                    stepsZ = 0
                else:
                    stepsZ = int(movestepsZ*2000)
                    self.moveDown(stepsZ)
                    time.sleep(3)
            
            ###### X-axis Zaber positioner ######
            if i == 0:
                steps = 0
            else:
                if stepsX_cal[i,0] == 'home':
                    self.rightToHome()
                else:
                    if stepsX_cal[i-1,0] == 'home':
                        movesteps = -(float(stepsX_cal[i,0])-lenX)
                    else:
                        movesteps = -(float(stepsX_cal[i,0])-float(stepsX_cal[i-1,0]))

                    steps = int(movesteps*2000)
                    self.moveLeft(steps)
            
            time.sleep(1)
            
            ###### Syringe pump ######
            direction = stepsX_cal[i,2]
            flowrate = stepsX_cal[i,3]
            targettime = stepsX_cal[i,4]
            
            ###### NiDAQ ######
            filenameT = 'X'+str(stepsX_cal[i,0])+'Z'+str(stepsX_cal[i,1])+'_temperature_waveform.txt'
            filename = 'X'+str(stepsX_cal[i,0])+str(stepsX_cal[i,2])+str(stepsX_cal[i,3])+'mlmin'\
                       +str(stepsX_cal[i,4])+'s'+'Z'+str(stepsX_cal[i,1])+'_waveform.txt'

            operation = True
            while operation:
                me = threading.Thread(target=measure(flowrate, direction, targettime, filename, filenameT))
                me.start()
                me.join()
        
                lp = filter_lowpass_omega(filename,flowrate,targettime)

                if abs(lp[0]) >= 100:
                    operation = False
                else:
                    print ('Suffering an issue of syringe pump, repeat measurement.')


            df2 = pd.DataFrame({'X' : stepsX_cal[i,0],
                    'Z' : stepsX_cal[i,1],
                    'direction' : stepsX_cal[i,2],
                    'flowrate' : stepsX_cal[i,3],
                    'targettime' : stepsX_cal[i,4],
                    'pressure mean': [lp[0]],
                    'pressure std': [lp[1]],
                    'Cd mean': [lp[2]],
                    'Cd std': [lp[3]],
                    'Cd se': [lp[4]],
                    'Cd n': [lp[5]]})
                    
            print (df2)
            df = pd.concat([df,df2])

            os.remove(filename)
            os.remove(filenameT)

        print (df)
        ffname = time.strftime('%Y%m%d')+'_'+time.strftime('%H%M%S')+'_calibration.csv'
        df.to_csv(ffname,index=False,sep=',')
        
        print ('All done.')

    def sideways(self, stepsZ_path, folder_data_user, cal_path, lenX, offset, pre_Max):
        # Display all rows
        pd.set_option('display.height', 1000)
        pd.set_option('display.max_rows', 1)
        pd.set_option('display.max_columns', 30)
        pd.set_option('display.width', 1000)
        
        stepsZ_list = np.array(pd.read_csv(stepsZ_path))
        cal_list = np.array(pd.read_csv(cal_path))
        print (stepsZ_list)
        
        wholeloop = stepsZ_list.shape[0]

        pre_recorded = 0
        for i in range(0,wholeloop):
            if i == 0:
                self.rightToHome() # X-axis zaber goes home for starting.
                recordX = 0 + offset # Compensate offset calculated from calibration
            else:
                if stepsZ_list[i,0] == stepsZ_list[i-1,0]:
                    recordX = recordX
                    if pre_recorded >= pre_Max:
                        print ('The loop is skipped, because measured pressure ('+str(pre_recorded)+') surpasses the maximum tolerance ('+str(pre_Max)+').')
                        continue
                else:
                    self.rightToHome() 
                    recordX = 0 + offset # Compensate offset calculated from calibration

            ###### Z-axis zaber positioner ######
            # Read Zaber's current position
            zr = open(folder_steps +'Zzaber_position.txt', "r")
            lines = zr.readlines()
            zr.close()
            z_record = lines[0]
            print (z_record)

            movestepsZ = (float(stepsZ_list[i,0])-float(z_record))
            stepsZ = -int(movestepsZ*2000)
            self.moveDown(stepsZ)

            # Start to record time, just immerse
            if i == 0:
                initialTime = time.clock()
                df = pd.DataFrame({'loop' : [],
                               'X' : [],
                               'Z' : [],
                               'flow rate' : [],
                               'target time' : [],
                               'E_pressure mean': [],
                               'E_pressure std': [],
                               'E_Cd mean': [],
                               'E_Cd std': [],
                               'E_Cd se': [],
                               'E_estimated h': [],
                               'E_estimated h std': [],
                               'E_thickness': [],
                               'E_thickness se': [],
                               'S_pressure mean': [],
                               'S_pressure std': [],
                               'S_Cd mean': [],
                               'S_Cd std': [],
                               'S_Cd se': [],
                               'S_estimated h': [],
                               'S_estimated h std': [],
                               'S_thickness': [],
                               'S_thickness se': [],
                                   'E_operation time': [],
                                   'S_operation time': [],
                                   'sample number': [],
                                   'Temperature mean': [],
                                   'Temperature std': []})
            else:
                if stepsZ_list[i,0] == stepsZ_list[i-1,0]:
                    initialTime = initialTime
                    df = df
                else:
                    initialTime = time.clock()
                    df = pd.DataFrame({'loop' : [],
                               'X' : [],
                               'Z' : [],
                               'flow rate' : [],
                               'target time' : [],
                               'E_pressure mean': [],
                               'E_pressure std': [],
                               'E_Cd mean': [],
                               'E_Cd std': [],
                               'E_Cd se': [],
                               'E_estimated h': [],
                               'E_estimated h std': [],
                               'E_thickness': [],
                               'E_thickness se': [],
                               'S_pressure mean': [],
                               'S_pressure std': [],
                               'S_Cd mean': [],
                               'S_Cd std': [],
                               'S_Cd se': [],
                               'S_estimated h': [],
                               'S_estimated h std': [],
                               'S_thickness': [],
                               'S_thickness se': [],
                                   'E_operation time': [],
                                   'S_operation time': [],
                                   'sample number': [],
                                   'Temperature mean': [],
                                   'Temperature std': []})


            time.sleep(2)
            # Write Zaber's current position    
            new_position = stepsZ_list[i,0]
            zw = open(folder_steps + 'Zzaber_position.txt', "w")
            zw.write(str(new_position))
            zw.close()  



            loop = int(stepsZ_list[i,10])
            flowrate = stepsZ_list[i,3]
            targettime = stepsZ_list[i,4]
            pre_approach = stepsZ_list[i,5]
            move_approach = stepsZ_list[i,6]
            pre_away = stepsZ_list[i,7]
            move_away = stepsZ_list[i,8]

            time.sleep(stepsZ_list[i,1]) # Wait for starting.
            movestepsX = 0
            hE = 0
            hS = 0

            
            for j in range(0,loop):                
                loopnumber = j+1              
                print ('Start '+str(loopnumber)+' of '+str(loop)+' loops.')
                ###### X-axis zaber positioner ######
                if j == 0:
                    if i > 0 and stepsZ_list[i,0] == stepsZ_list[i-1,0]:
                        movestepsX = stepsZ_list[i,2]-stepsZ_list[i-1,2]
                    else:
                        movestepsX = stepsZ_list[i,2]
                else:
                    movestepsX = movestepsX
                    
                stepsX = -int(movestepsX*2000)
                self.moveLeft(stepsX)
                recordX = recordX+movestepsX
                time.sleep(1)

                ###### filename for temperature measurement ######
                filenameT = folder_data_user+'Z'+str(stepsZ_list[i,0])+'X'+str(recordX)+'loop'+str(j+1)+'_temperature_waveform.txt'

                ###### Measurement for ejection pressure (Temperature) ######
                ejection = True
                while ejection:       
                    filenameE = folder_data_user+'Z'+str(stepsZ_list[i,0])+'X'+str(recordX)+'E'+str(flowrate)+'mlmin'\
                           +str(targettime)+'sloop'+str(j+1)+'_waveform.txt'
                    meE = threading.Thread(target=measure(flowrate,'E', targettime, filenameE, filenameT))
                    meE.start()
                    meE.join()
                    lpE = filter_lowpass_omega(filenameE,flowrate,targettime)
                    if abs(lpE[0]) >= 100:
                        ejection = False
                    else:
                        print ('Suffering an issue of syringe pump, repeat ejection measurement.')
                endTimeE = time.clock()-initialTime
                        
                
                ###### Measurement for suction pressure (Temperature) ######
                suction = True
                while suction:
                    filenameS = folder_data_user+'Z'+str(stepsZ_list[i,0])+'X'+str(recordX)+'S'+str(flowrate)+'mlmin'\
                           +str(targettime)+'sloop'+str(j+1)+'_waveform.txt'
                    meS = threading.Thread(target=measure(flowrate,'S', targettime, filenameS, filenameT))
                    meS.start()
                    meS.join()
                    lpS = filter_lowpass_omega(filenameS,flowrate,targettime)
                    if abs(lpS[0]) >= 100:
                        suction = False
                    else:
                        print ('Suffering an issue of syringe pump, repeat suction measurement.')
                
                endTimeS = time.clock()-initialTime

                
                ###### Analysis of temperature data ######
                lpT = temperature(filenameT)

                ###### Interpolation ######
                fcE = interpolate.interp1d(cal_list[:,1], cal_list[:,0], kind='linear', bounds_error=False, fill_value='extrapolate')
                fcS = interpolate.interp1d(cal_list[:,2], cal_list[:,0], kind='linear', bounds_error=False, fill_value='extrapolate')
                hE = fcE(lpE[2])
                hS = fcS(lpS[2])


                ### Calculate standard deviation from interpolation ###
                acc = 45E-3 # positioner's accuracy (mm)

                if hE <= min(cal_list[:,0]):
                    indE = np.argmin(cal_list[:,0])
                    dydxE = (cal_list[indE,0]-hE)/(cal_list[indE,1]-lpE[2])
                    interpolateSDE = (acc**2+(dydxE**2)*(cal_list[indE,3]**2+lpE[3]**2))**0.5
                elif hE >= max(cal_list[:,0]):
                    indE = np.argmax(cal_list[:,0])
                    dydxE = (hE-cal_list[indE,0])/(lpE[2]-cal_list[indE,1])
                    interpolateSDE = (acc**2+(dydxE**2)*(cal_list[indE,3]**2+lpE[3]**2))**0.5
                else:
                    indE = np.array(np.where(cal_list[:,0] < hE))
                    dydxE = (cal_list[indE[0,0],0]-cal_list[indE[0,0]-1,0])/(cal_list[indE[0,0],1]-cal_list[indE[0,0]-1,1])   
                    interpolateSDE = (2*acc**2+(dydxE**2)*(cal_list[indE[0,0]-1,3]**2+cal_list[indE[0,0],3]**2+lpE[3]**2))**0.5

                thicknessEse = interpolateSDE/(lpE[5]**0.5)
                

                if hS <= min(cal_list[:,0]):
                    indS = np.argmin(cal_list[:,0])
                    dydxS = (cal_list[indS,0]-hS)/(cal_list[indS,2]-lpS[2])
                    interpolateSDS = (acc**2+(dydxS**2)*(cal_list[indS,4]**2+lpS[3]**2))**0.5
                elif hS >= max(cal_list[:,0]):
                    indS = np.argmax(cal_list[:,0])
                    dydxS = (hS-cal_list[indS,0])/(lpS[2]-cal_list[indS,2])
                    interpolateSDS = (acc**2+(dydxS**2)*(cal_list[indS,4]**2+lpS[3]**2))**0.5
                else:
                    indS = np.array(np.where(cal_list[:,0] < hS))
                    dydxS = (cal_list[indS[0,0],0]-cal_list[indS[0,0]-1,0])/(cal_list[indS[0,0],2]-cal_list[indS[0,0]-1,2])   
                    interpolateSDS = (2*acc**2+(dydxS**2)*(cal_list[indS[0,0]-1,4]**2+cal_list[indS[0,0],4]**2+lpS[3]**2))**0.5

                thicknessSse = interpolateSDS/(lpS[5]**0.5)



       
                thicknessE = lenX+recordX-hE
                thicknessS = lenX+recordX-hS

                ###### Adjust clearance ######
                print ('Measured suction pressure: '+str(abs(lpS[0]))+' Pa.')
                if abs(lpS[0]) < pre_approach:
                    movestepsX = -move_approach
                elif abs(lpS[0]) > pre_away:
                    movestepsX = move_away
                else:
                    movestepsX = 0


                df2 = pd.DataFrame({'loop' : loopnumber,
                                    'X' : recordX,
                                    'Z' : stepsZ_list[i,0],
                                    'flow rate' : flowrate,
                                    'target time' : targettime,
                                    'E_pressure mean': [lpE[0]],
                                    'E_pressure std': [lpE[1]],
                                    'E_Cd mean': [lpE[2]],
                                    'E_Cd std': [lpE[3]],
                                    'E_Cd se': [lpE[4]],
                                    'E_estimated h': hE,
                                    'E_estimated h std': interpolateSDE,
                                    'E_thickness': thicknessE,
                                    'E_thickness se': thicknessEse,
                                    'E_operation time': endTimeE,
                                    'S_pressure mean': [lpS[0]],
                                    'S_pressure std': [lpS[1]],
                                    'S_Cd mean': [lpS[2]],
                                    'S_Cd std': [lpS[3]],
                                    'S_Cd se': [lpS[4]],
                                    'S_estimated h': hS,
                                    'S_estimated h std': interpolateSDS,
                                    'S_thickness': thicknessS,
                                    'S_thickness se': thicknessSse,
                                    'S_operation time': endTimeS,
                                    'sample number': [lpS[5]],
                                    'Temperature mean': [lpT[0]],
                                    'Temperature std': [lpT[1]]})

                df2_show = pd.DataFrame({'loop' : loopnumber,
                                    'X' : recordX,
                                    'Z' : stepsZ_list[i,0],
                                    'E_pressure mean': [lpE[0]],
                                    'E_pressure std': [lpE[1]],
                                    'E_Cd mean': [lpE[2]],
                                    'E_Cd std': [lpE[3]],
                                    'E_estimated h': hE,
                                    'E_thickness': thicknessE,
                                    'E_operation time': endTimeE,
                                    'S_pressure mean': [lpS[0]],
                                    'S_pressure std': [lpS[1]],
                                    'S_Cd mean': [lpS[2]],
                                    'S_Cd std': [lpS[3]],
                                    'S_estimated h': hS,
                                    'S_thickness': thicknessS,   
                                    'S_operation time': endTimeS})


                         
                print (df2_show)
                os.remove(filenameE)
                os.remove(filenameS)
                os.remove(filenameT)

                time.sleep(stepsZ_list[i,9]) # Wait for next loop.
                print ('Wait '+str(stepsZ_list[i,9])+' s for next loop.')
                df = pd.concat([df,df2])

                # Save file for figure animation
                ani_name = folder_data + 'tempDataForAnimation.csv'
                df.to_csv(ani_name,index=False,sep=',')

                ###### Break while the measured pressure reaches the maximum tolerance ######
                pre_recorded = max(abs(lpE[0]),abs(lpS[0]))
                if pre_recorded > pre_Max:
                    print ('The loop is terminated, because measured pressure ('+str(pre_recorded)+') surpasses the maximum tolerance ('+str(pre_Max)+').')
                    break

            
            print (df)
            fname = folder_data_user+time.strftime('%Y%m%d')+'_'+time.strftime('%H%M%S')+'_Round'+str(i+1)+'_results.csv'
            df.to_csv(fname,index=False,sep=',')
            #os.remove(ani_name)
            
        self.rightToHome() # X-axis zaber goes home for ending.
        time.sleep(2)
        self.upToHome() # Z-axis zaber goes home for ending.
        new_position = 0
        zw = open(folder_steps+'Zzaber_position.txt', "w")
        zw.write(str(new_position))
        zw.close() 
        print ('All done.')



####################### PX409USBH #######################################################
def omega(filename, targetime):
    pport = COM12
    sampling_rate = 40 #Sampling rate
    samples_per_channel = (int(targetime)+4)*sampling_rate #Samples per channel 

    with PX409USBH.PX409(pport) as omega:
        print ('Omega starts.\n')
        dataOri = omega.pcClock(samples_per_channel)

    dataTime = np.linspace(0, samples_per_channel/sampling_rate, samples_per_channel)
    dataCal = dataOri[:,1]*100
    data = np.zeros((samples_per_channel,2))
    data[:,0] = dataTime
    data[:,1] = dataCal
    
    np.savetxt(filename, data, delimiter=',')
    print ('Omega finishes.\n')


################# Harvard Syringe Pump ############################################
def syringe_pump(flowrate, direction, targetime):
    synport = COM6
    diameter = diameter_syringe
    
    print ('Syringe pump starts ('+direction+' mode at '+str(flowrate)+' ml/min '+str(targetime)+'s). \n')
    with harvard.Chain(synport) as chain: 

        p11 = harvard.Pump(chain, address=0) 
        p11.setdiameter(diameter)  # mm

        if direction == 'E':
            p11.setflowrateinfuse(flowrate)
            p11.settargetime(targetime)
            if targetime > 0:
                p11.infuse()
        else:
            p11.setflowratewithdraw(flowrate)
            p11.settargetime(targetime)
            if targetime > 0:
                p11.withdraw()

        chain.close()
    print ('Syringe pump finishes.\n')
    

############# Low-pass Filter for OMEGA ##############################
def filter_lowpass_omega(filename,flowrate,targetime):

    stat = np.zeros((8))
    
    x = np.array(pd.read_csv(filename))
    pstatNumber = 80
    pstat = np.zeros((pstatNumber,2))
    for k in range(pstatNumber):
        pstat[k,0] = x[k,0]
        pstat[k,1] = x[k,1]
    bstat, astat = signal.butter(3, 1/20, 'lowpass')
    ystat = signal.filtfilt(bstat, astat, pstat[:,1])
    pstatMean = np.mean(ystat)
    pstatStd = np.std(ystat)
       
    cut = (int(targetime)-2)*40 
    start = filteredPoint*40
    cutx = np.zeros((cut,2))    
    for j in range(cut):
        cutx[j,0] = x[start+j,0]
        cutx[j,1] = x[start+j,1]
    b, a = signal.butter(3, 1/20, 'lowpass')
    y = signal.filtfilt(b, a, cutx[:,1])

    m = flowrate/1000000*rho/60 #Unit: kg/s
    dt = 0.001
    cd = 4*m/(3.1415*dt**2*(2*rho*abs(y-pstatMean))**0.5)
    stat[0] = np.mean(y-pstatMean)
    stat[1] = np.std(y-pstatMean)
    stat[2] = np.mean(cd)
    stat[3] = np.std(cd)
    stat[4] = stats.sem(cd) # Standard error of measurement    
    stat[5] = len(cd[:]) # Number of samples
    stat[6] = pstatMean # Static pressure mean
    stat[7] = pstatStd # Static pressure standard deviation

    return stat


############### Measurement ###################### 
def measure(flowrate, direction, targetime, filename, filenameThermo):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    #with concurrent.futures.ProcessPoolExecutor() as executor:
        sp = executor.submit(syringe_pump, flowrate, direction, targetime)
        nithermo = executor.submit(nidaqThermo, filenameThermo)
        time.sleep(3)
        #ni = executor.submit(nidaq, filename, targetime)
        om = executor.submit(omega, filename, targetime)

    

############ Thermocouple nidaq ##############################
def nidaqThermo(filename):
    niport = "Dev3/ai1"
    sampling_rate = 100 #Sampling rate
    samples_per_channel = sampling_rate #Samples per channel 

    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(niport, terminal_config=TerminalConfiguration.DIFFERENTIAL, min_val=-5.0, max_val=5.0, units=VoltageUnits.VOLTS)
        task.timing.cfg_samp_clk_timing(sampling_rate, active_edge=Edge.RISING, sample_mode=AcquisitionType.FINITE, samps_per_chan=samples_per_channel)

        d1 = np.linspace(0,samples_per_channel/sampling_rate,samples_per_channel)
        print ('Thermocouple starts.\n')
        d2 = task.read(number_of_samples_per_channel=samples_per_channel)
        d3 = np.zeros((samples_per_channel,2))
        d3[:,0] = d1
        for i in range(len(d2)):
            d3[i,1] = d2[i]
        
        np.savetxt(filename, d3, delimiter=',')
        print ('Thermocouple finishes.\n')    


############# Thermocouple ###################################
def temperature(filename):
    sampling_rate = 100
    data = np.zeros((2))    
    x = np.array(pd.read_csv(filename))
    xCal = np.zeros((len(x[:,1])))
    for i in range (len(xCal)):
        xCal[i] = x[i,1]*1000    
    
    b, a = signal.butter(3, 1/(sampling_rate/2), 'lowpass')
    y = signal.filtfilt(b, a, xCal)
    data[0] = np.mean(y)
    data[1] = np.std(y)
    print ('Mean temperature: '+str(data[0])+', Std: '+str(data[1])+'.\n')
    
    return data






# Buttons' functions start
def moveLeft():
    with Zaber() as zaber:
        #Read Zaber's current position
        zr = open(folder_steps + 'Xzaber_position.txt', "r")
        lines = zr.readlines()
        zr.close()
        z_record = lines[0]
            
        movesteps = float(e1.get())
        steps = int(-movesteps*2000)
        zaber.moveLeft(steps)
            
            
        #Write Zaber's current position    
        new_position = float(z_record)+movesteps
        zw = open(folder_steps + 'Xzaber_position.txt', "w")
        zw.write(str(new_position))
        zw.close()
    print (e1.get())


def rightToHome():
    with Zaber() as zaber:
        zaber.rightToHome()
        # Write Zaber's current position    
        new_position = 0
        zw = open(folder_steps + 'Xzaber_position.txt', "w")
        zw.write(str(new_position))
        zw.close()
        
    print ('go home')

def moveDown():
    with Zaber() as zaber:
        # Read Zaber's current position
        zr = open(folder_steps + 'Zzaber_position.txt', "r")
        lines = zr.readlines()
        
        zr.close()
        z_record = lines[0]

        movesteps = float(e2.get())
        steps = int(-movesteps*2000)
        zaber.moveDown(steps)

        # Write Zaber's current position    
        new_position = float(z_record)+ movesteps
        zw = open(folder_steps + 'Zzaber_position.txt', "w")
        zw.write(str(new_position))
        zw.close()
    

    print (e2.get())

def upToHome():
    with Zaber() as zaber:
        zaber.upToHome()
        # Write Zaber's current position    
        new_position = 0
        zw = open(folder_steps + 'Zzaber_position.txt', "w")
        zw.write(str(new_position))
        zw.close()



    print ('go home')

def calibration():
    
    with Zaber() as zaber:
        stepsX_path = e3.get() + e5.get()
        zaber.calibration(stepsX_path)
    
    print ('calibration')


def sideways():
    
    with Zaber() as zaber:
        stepsZ_path = e3.get() + e6.get()
        folder_data_user = e4.get()
        cal_path = e3.get() + e7.get()
        lenX = float(e8.get())
        offset = float(e9.get())
        pre_Max = float(e10.get())
        zaber.sideways(stepsZ_path, folder_data_user, cal_path, lenX, offset, pre_Max)
    
   

    

# Buttons start
b1 = ttk.Button(tab1, text = 'Move', width = 15, command = moveLeft).place(x = 150, y = 65)
b2 = ttk.Button(tab1, text = 'Go Home', width = 15, command = rightToHome).place(x = 255, y = 65)

b3 = ttk.Button(tab1, text = 'Move', width = 15, command = moveDown).place(x = 150, y = 165)
b4 = ttk.Button(tab1, text = 'Go Home', width = 15, command = upToHome).place(x = 255, y = 165)

b5 = ttk.Button(tab1, text = 'Run "Calibration mode"', width = 30, command = calibration).place(x = 150, y = 380)

b6 = ttk.Button(tab1, text = 'Run "Measurement mode"', width = 30, command = sideways).place(x = 150, y = 620)



ani = animation.FuncAnimation(f, animate, interval=1000)
window.mainloop()
