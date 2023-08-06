from unicodedata import name
import matplotlib.pyplot as plt
import numpy as np


# --------------------------------------------------------------------------------------------
# projectiles --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


# * simple projectile ------------------

# TODO: add vx and vy vectors input ad parameters
# TODO: and if u is given, reject vx and vy else find angle
# TODO: and u from vx and vy...
class simple_projectile:

    def __init__(self, u = None, theta = None, base_height = None, g = 9.8, degree = True):

        self.initial_velocity = u
        
        self.angle = theta
        if degree == True:
            self.angle = np.radians(theta)
        else:
            self.angle = theta
            
        self.acceleration_g = g
        self.h = base_height
        


    def range(self):
        if self.h == None:
            r = ((self.initial_velocity ** 2)*np.sin(2*self.angle))/self.acceleration_g
            return r
        else:
            #
            # d = ucos@(usin@ + root(u^2sin^2@+2gh))
            #       g
            po = (self.initial_velocity*np.cos(self.angle))/self.acceleration_g
            pt = (self.initial_velocity**2)*((np.sin(self.angle))**2)+(2*self.acceleration_g*self.h)
            pth = (self.initial_velocity*np.sin(self.angle))+np.sqrt(pt)
            r = po*pth
            return r
            

    def round_range(self, round_index = 0, final = 0):
        i = np.round(self.initial_velocity, round_index)
        a = np.round(np.sin(2*self.angle), round_index)
        g = np.round(self.acceleration_g, round_index)
        if self.h == None:
            raw_r = ((i**2)*a)/g
            r = np.round(raw_r, final)
            return r
        else:
            hi = np.round(self.h, round_index)
            po = (i*np.round(np.cos(self.angle), round_index))/g
            pt = (i**2)*np.round(((np.sin(self.angle))**2), round_index)+np.round((2*self.acceleration_g*self.h), round_index)
            pth = (i*np.round(np.sin(self.angle), round_index))+np.round(np.sqrt(pt), round_index)
            raw_r = po*pth
            r = np.round(raw_r, final)
            return r



    def time(self):
        if self.h == None:
            t = (2*(self.initial_velocity*np.sin(self.angle)))/self.acceleration_g
            return t
        else:
            to = self.initial_velocity*np.sin(self.angle)
            ts = np.sqrt((self.initial_velocity*np.sin(self.angle))**2)
            tf = 2*self.acceleration_g*self.h
            t = (to+ts+tf)/self.acceleration_g
            return t

 
    def round_time(self, round_index = 0, final = 0):
        i = np.round(self.initial_velocity, round_index)
        a = np.round(np.sin(self.angle), round_index)
        g = np.round(self.acceleration_g, round_index)
        if self.h == None:
            rt = (2*(i*a))/g
            t = np.round(rt, final)
            return t
        else:
            to = i*a
            ts = np.round(np.sqrt((i*a)**2), round_index)
            tf = 2*g*np.round(self.h, round_index)
            rt = np.round(((to+ts+tf)/self.acceleration_g), round_index)
            t = np.round(rt, final)
            return t


    def height(self):
        if self.h == None:
            h = ((self.initial_velocity*np.sin(self.angle))**2)/(2*self.acceleration_g)
            return h
        else:
            h2 = ((self.initial_velocity*np.sin(self.angle))**2)/(2*self.acceleration_g)
            h = h2 + self.h
            return h


    def round_height(self, round_index = 0, final = 0):
        i = np.round(self.initial_velocity, round_index)
        a = np.round(np.sin(self.angle), round_index)
        g = np.round(self.acceleration_g, round_index)
        if self.h == None:
            rh = ((i*a)**2)/(2*g)
            h = np.round(rh, final)
            return h
        else:
            h2 = ((i*a)**2)/(2*g)
            rh = h2 + np.round(self.h, round_index)
            h = np.round(rh, final)
            return h




# * projectile with air drag ----------

# TODO: make complete class
# TODO: note and make formulas...
class projectile:
    def __init__(self) -> None:
        pass



# --------------------------------------------------------------------------------------------
# small equations ----------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


# * some rst practice
"""

#:param int num1: The first number
#:returns: The answer
#:rtype: int
#This method will be used to subtract num2 from num1
#
#:param int num1: The first number
#:param int num2: The second number
#
#:returns: The answer
#
#:rtype: int


    this function claculates acceleration due to gravity when object is near
    planet, you can set all arguments or just choose planet from preset planets
     
    
    Args:
        heigt (float, optional): it stores the height of object above ground. Defaults to None.
        mass (float, optional): it stores the mass of planet. Defaults to None.
        radius (float, optional): it stores the radius of planet. Defaults to None.
        preset (str, optional): it stores name of planet as a string. Defaults to None.
        frompreset (bool, optional): mark it as True if you want to calculate data from presets. Defaults to False.

    Raises:
        Exception: it raises exception if value of ```preset``` given
            is invalid, valid values are
            'sun','mercuery','venus','earth','moon','mars','ceres','jupiter',
            'lo','europa','ganymede','callisto','saturn','titan','uranus',
            'titania','oberon','neptune','triton','pluto','eiris'

    Returns:
        float: it returns acceleration due to gravity of different planets when object is not too far
    
    .. code-block:: python
        # **example**
        import pysvl as sv
        acceleration_moon = sv.g(preset='moon')
        acceleration_earth = sv.g(preset='earth')
        acceleration_above_the_ground = sv.g(height=20000, preset='earth', frompreset=True)
        print(acceleration_moon)
        print(acceleration_earth)
        print(acceleration_above_the_ground)
    
    **output**
    
    .. code-block:: python
        1.625
        9.806
        
    ----
"""


# * calculate acceleration due to gravity (g) -------
# TODO: in future or someday, remove use of frompreset,
# TODO: if preset is set, then automaticly use frompreset(True)
# TODO: refine code , only one if else
# ! critical bugfix, related to height (param)
# ! error : -->
# ! Traceback (most recent call last):
# !  File "f:\study\class_12\computer_cs_12\python_12\pysvl_lib\test_pysvl.py", line 181, in <module>
# !    acceleration_above_the_ground = sv.g(height=20000, preset='earth')
# !  File "f:\study\class_12\computer_cs_12\python_12\pysvl_lib\pysvl\main.py", line 225, in g
# !    eq = (G*mass)/((radius+height)**2)
# !TypeError: unsupported operand type(s) for *: 'float' and 'NoneType'
def g(height = None, mass = None, radius = None, preset = None, frompreset = False):
    ag = None
    if preset == None:
        ag = 9.8
    else:
        gd = {'sun':274.1,'mercuery':3.703,'venus':8.872,'earth':9.806,
              'moon':1.625,'mars':3.728,'ceres':0.28,'jupiter':25.93,
              'lo':1.789,'europa':1.314,'ganymede':1.426,'callisto':1.24,
              'saturn':11.19,'titan':1.3455,'uranus':9.01,'titania':0.379,
              'oberon':0.347,'neptune':11.28,'triton':0.779,'pluto':0.610,
              'eiris':0.8}
        
        try:
            ag = gd[preset.lower()]
        except:
            raise Exception(str('nothing named '+preset+' found in database\n\
                database: '+str(gd)))
    
    if height == None:
        return ag
    else:
        if frompreset == True:
            rd = {'sun':696340,'mercuery':2439.7,'venus':6051.8,'earth':6371,
                  'moon':1737.4,'mars':3389.5,'ceres':473,'jupiter':69911,
                  'lo':1821.6,'europa':1560.8,'ganymede':2634.1,'callisto':2410.3,
                  'saturn':58232,'titan':2574.7,'uranus':25362,'titania':788.4,
                  'oberon':761.4,'neptune':24622,'triton':1353.4,'pluto':1188.3,
                  'eiris':1163}
            radius2 = rd[preset]*1000
            eq = ag*(1-((2*height)/radius2))
            return eq
        else:
            G = 0.000000000066743
            eq = (G*mass)/((radius+height)**2)
            return eq








if __name__ == "__main__":
    print('avrage acceleration due to gravity of earth near surface is ',g(preset='earth'))
    print('if you see this message correctly, then library is sucessfully runned')
