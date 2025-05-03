import numpy as np
from pygame import *

"""
MEASUREMENTS:

length: px
time: s
mass: kg
force: kg*px/s^2 = N
density: kg/px^2
area: px^2

"""




class Constants:
    def __init__(self):
        self.GRAV_ACCEL = Vector2(0, 0.0981) # px/s^2
        self.DRAG_COEFICCIENT = 0.47 # dimensionless
        self.GRAVITATIONAL = 6.67430e-1/2  # px^3 kg^-1 s^-2
        self.COULOUMB = 8.9875517873681764e9  # px^2 kg^-1 s^-4 
        self.MIN_DISTANCE = 10  # px
        self.WALL_BOUNCE = 0.3 # dimensionless


constants = Constants()


class Forces:
    def drag(self, velocity):
        """Calculate drag force."""
        return -constants.DRAG_COEFICCIENT * velocity * np.linalg.norm(velocity) 
    
    def gravity(self, mass): 
        """Calculate gravitational force."""
        return mass * constants.GRAV_ACCEL
    
    def grav_attraction(self, mass1, mass2, distance_vector):
        """Calculate gravitational attraction between two masses as a vector."""
        distance = np.linalg.norm(distance_vector)
        if distance < constants.MIN_DISTANCE:
            return Vector2(0, 0)
        force_magnitude = (constants.GRAVITATIONAL * mass1 * mass2) / (distance**2)
        return force_magnitude * (distance_vector / distance)
    
    
    def spring(self, k, displacement_vector):
        """Calculate spring force as a vector."""
        return -k * displacement_vector
    
    def collision(self, velocity1, velocity2, mass1, mass2, overlap_vector, bounce):
        """Calculate collision force."""
        # velocity 1 is the particle that the force is applied to
        momentum = (velocity1*mass1 + velocity2*mass2)/2
        momentum_scalar = momentum.length()
        return momentum_scalar * overlap_vector * bounce

    
forces = Forces()