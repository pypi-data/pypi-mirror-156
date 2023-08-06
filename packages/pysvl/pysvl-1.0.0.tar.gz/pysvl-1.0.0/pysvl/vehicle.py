# pysvl.vehicle

import matplotlib.pyplot as plt
import numpy as np


class pslv:

    def __init__(self):
        """
        creates the data for class pslv
        """
        self.varient = 'PSLV-XL'
        self.varients = ('PSLV-G', 'PSLV - CA', 'PSLV - XL')
        self.varients_info = {'pslv_g':'6 strap-on rocket of 9 tonnes','pslv_xl':'6 strap-on rocket of 12 tonnes','pslv_ca':'no strap-on rockets'}

        self.stages = 4
        self.stage_types = {1:{'name':'ps1', 'thrust':4800, 'thrustN':4800000, 'fuel':'htbp', 'engine':'s139','engineN':1, 'strap_on':(6, 'htbp', 719, 719000), 'state':'solid', 'pitch':'SITVC', 'yaw':'SITVC', 'roll':'RCT and SITVC in 2 PSOMs'},
                            2:{'name':'ps2', 'thrust':799, 'thrustN':799000, 'fuel':'udmh+n2o4', 'engine':'vikas','engineN':1, 'strap_on':(0, 'no strap on booster', 0, 0), 'state':'liquid', 'pitch':'Engine Gimbal', 'yaw':'Engine Gimbal', 'roll':'HRCM Hot Gas Reaction Control Motor'},
                            3:{'name':'ps3', 'thrust':240, 'thrustN':240000, 'fuel':'htbp', 'engine':'--na--','engineN':1, 'strap_on':(0, 'no strap on booster', 0, 0), 'state':'solid', 'pitch':'Nozzle Flex', 'yaw':'Nozzle Flex', 'roll':'PS4 RCS'},
                            4:{'name':'ps4', 'thrust':15.2, 'thrustN':15200, 'fuel':'mmh+mon', 'engine':'PS-4 (7.6 KN)', 'engineN':2, 'strap_on':(0, 'no strap on booster', 0, 0), 'state':'liquid', 'pitch':'Engine Gimbal', 'yaw':'Engine Gimbal', 'roll':'PS4 RCS'}}

        self.strap_on = {'thrust':719, 'thrustN':719000, 'fuel':'htbp'}
        
        self.height = 44
        self.diameter = 2.8
        self.lift_off_mass = 320000
        self.lift_off_massT = 320





    def c25_mom_flight_profile(self):

        plt.figure(num='pslv c25', figsize=(11,6))
        
        # altitude graph
        # time
        x = np.array([0, 112.14, 112.34, 201.14, 263.00, 264.20, 582.76, 2099.52, 2616.30, 2653.30])
        # real alt.
        y = np.array([0.0238 , 58.0, 58.17, 114.081, 132.271, 132.456, 195.163, 297.587, 336.237, 375.869])
        # predicted alt.
        pdy = np.array([0.0238, 57.687, 57.854, 113.173, 132.311, 132.531, 194.869, 271.317, 342.515, 383.388])
        # label list
        lbl = ['real altitude','predicted altitude']

        plt.subplot(1,2,1)
        plt.title('pslv c-25 altitude-time garph')
        plt.xlabel('time in seconds')
        plt.ylabel('altitude in km')
        plt.plot(x, y, color = 'b', ls='-', marker = 'o', ms=4)
        plt.plot(x, pdy, color = 'y', ls='-.', marker = '+', ms=5)
        plt.legend(lbl, loc ="lower right")

        # velocity graph
        # real vel.
        y2 = np.array([451.89, 2413.66, 2413.48, 3664.602, 5380.776, 5380.835, 7740.523, 7620.510, 9840.126, 9808.942])
        # predicted vel.
        pdy2 = np.array([451.89, 2387.64, 2387.14, 3624.90, 5379.33, 5378.95, 7730.88, 7642.04, 9833.49, 9803.62])
        # label list
        lbl2 = ['real Inertial velocity','predicted Inertial velocity']

        plt.subplot(1,2,2)
        plt.title('pslv c-25 velocity-time garph')
        plt.xlabel('time in seconds')
        plt.ylabel('Inertial velocity in m/s')
        plt.plot(x, y2, color = 'b', ls='-', marker = 'o', ms=4)
        plt.plot(x, pdy2, color = 'y', ls='-.', marker = '+', ms=5)
        plt.legend(lbl2, loc ="lower right")


        
        plt.subplots_adjust(right = 0.98, left = 0.06, hspace=0.55, wspace=0.21)
        plt.show()

        

