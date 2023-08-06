# pysvl.realtime
# module for fast calculations
import math

# --------------------------------------------------------------------------------------------
# projectiles --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


# simple projectile --------------------

class simple_projectile:

    def __init__(self, u = None, theta = None, base_height = None, g = 9.8):

        self.initial_velocity = u
        self.angle = theta
        self.acceleration_g = g
        self.h = base_height
        


    def range(self):
        if self.h == None:
            r = ((self.initial_velocity ** 2)*math.sin(2*self.angle))/self.acceleration_g
            return r
        else:
            po = (self.initial_velocity*math.cos(self.angle))/self.acceleration_g
            pt = (self.initial_velocity**2)*((math.sin(self.angle))**2)+(2*self.acceleration_g*self.h)
            pth = (self.initial_velocity*math.sin(self.angle))+math.sqrt(pt)
            r = po*pth
            return r
            


    def time(self):
        if self.h == None:
            t = (2*(self.initial_velocity*math.sin(self.angle)))/self.acceleration_g
            return t
        else:
            to = self.initial_velocity*math.sin(self.angle)
            ts = np.sqrt((self.initial_velocity*math.sin(self.angle))**2)
            tf = 2*self.acceleration_g*self.h
            t = (to+ts+tf)/self.acceleration_g
            return t


 
    def height(self):
        if self.h == None:
            h = ((self.initial_velocity*math.sin(self.angle))**2)/(2*self.acceleration_g)
            return h
        else:
            h2 = ((self.initial_velocity*math.sin(self.angle))**2)/(2*self.acceleration_g)
            h = h2 + self.h
            return h


