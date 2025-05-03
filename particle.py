from pygame import *
from forces import *
import math
import random

def isnt_none(value):
    """Check if the value is not None."""
    return value is not None

class ForceManager:
    def __init__(self, particle):
        self.particle: Particle = particle
    
    def apply(self):
        pass

class DragManager(ForceManager):
    def apply(self):
        drag_force = forces.drag(self.particle.velocity)
        self.particle.apply_force(drag_force)

class GravityManager(ForceManager):
    def apply(self):
        gravity_force = forces.gravity(self.particle.mass)
        self.particle.apply_force(gravity_force)

class GravAttractionManager(ForceManager):
    def apply(self):
        for particle in self.particle.system.particles:
            if particle != self.particle:
                distance_vector = particle.position - self.particle.position
                distance_normal = distance_vector.normalize() if distance_vector.length() > constants.MIN_DISTANCE else Vector2(0, 0)
                distance = distance_vector.length()
                distance_vector = distance_normal * (distance - self.particle.radius - particle.radius)

                if distance > constants.MIN_DISTANCE:
                    force = forces.grav_attraction(self.particle.mass, particle.mass, distance_vector)
                    self.particle.apply_force(force)

class CollisionManager(ForceManager):
    def apply(self):
        for particle in self.particle.system.particles:
            if particle != self.particle:
                distance_vector = particle.position - self.particle.position
                distance_normal = distance_vector.normalize() if distance_vector.length() > constants.MIN_DISTANCE else Vector2(0, 0)
                distance = distance_vector.length()

                if distance < self.particle.radius + particle.radius:
                    overlap = (self.particle.radius + particle.radius) - distance
                    force = forces.collision(self.particle.velocity, particle.velocity, self.particle.mass, particle.mass, distance_normal * overlap, self.particle.bounce)
                    particle.apply_force(force)


class ScreenCollisionManager(ForceManager):
    def apply(self):
        bounding_box = ((self.particle.radius, self.particle.system.screen_dimensions[0] - self.particle.radius), (self.particle.radius, self.particle.system.screen_dimensions[1] - self.particle.radius))
        if self.particle.position.x < bounding_box[0][0] or self.particle.position.x > bounding_box[0][1]:
            self.particle.velocity.x *= -self.particle.bounce
            self.particle.position.x = max(0, min(self.particle.position.x, self.particle.system.screen_dimensions[0]))
        if self.particle.position.y < bounding_box[1][0] or self.particle.position.y > bounding_box[1][1]:
            self.particle.velocity.y *= -self.particle.bounce
            self.particle.position.y = max(0, min(self.particle.position.y, self.particle.system.screen_dimensions[1]))

class Particle:
    def __init__(self, x, y, system, force_managers: list, color=[random.randint(0, 255) for _ in range(3)], radius=None, mass=5.0, density=1.0, bounce = 0.3, trail_length_coef=2.5):
        """
        Initialize a Particle instance.

        Parameters:
        x (float): The x-coordinate of the particle's position.
        y (float): The y-coordinate of the particle's position.
        radius (float, optional): The radius of the particle. Defaults to None.
        mass (float, optional): The mass of the particle. Defaults to 5.0.
        density (float, optional): The density of the particle. Defaults to 1.0.
        color (tuple, optional): The RGB color of the particle. Defaults to (255, 255, 255).
        """
        self.position = Vector2(x, y)
        self.previous_position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.color = color
        self.update_properties(radius, mass, density)
        self.system: ParticleSystem = system
        system.particles.append(self)
        self.force_managers = [manager_class(self) for manager_class in force_managers]
        self.trail_length_coef = trail_length_coef
        self.bounce = bounce

    def get_area(self):
        return math.pi * self.radius**2

    def update_properties(self, radius=None, mass=None, density=None):
        radius_given = radius is not None
        mass_given = mass is not None
        density_given = density is not None

        if radius_given and density_given and mass_given:
            if not density == mass / (math.pi * radius**2):
                raise ValueError("Inconsistent values: mass, radius, and density do not match.")
                
            self.radius = radius
            self.mass = mass
            self.density = density
        
        elif radius_given and mass_given:
            self.density = mass / math.pi * radius**2
            self.radius = radius
            self.mass = mass
        
        elif mass_given and density_given:
            self.radius = math.sqrt(mass / (math.pi * density))
            self.density = density
            self.mass = mass
        
        elif density_given and radius_given:
            self.mass = density * math.pi * radius**2
            self.density = density
            self.radius = radius


    def apply_force(self, force):
        """Apply a force to the particle."""
        acceleration = force / self.mass
        self.velocity += acceleration

    def update(self):
        for manager in self.force_managers:
            manager.apply()

        self.previous_position = self.position.copy()
        self.position += self.velocity

    def draw_dot(self, screen):
        draw.circle(screen, self.color, self.position, self.radius)

    def draw_trail(self,screen):
        darkened_color = tuple(max(0, int(c * 0.7)) for c in self.color)
        trail_normal = (self.previous_position - self.position).normalize() if (self.previous_position - self.position).length() > 0 else Vector2(0, 0)
        trail_length = (self.previous_position - self.position).length()*self.trail_length_coef + self.radius
        trail_vector = trail_normal * trail_length
        draw.line(screen, darkened_color, self.position, self.position+trail_vector, max(1, (self.radius // 3) * 2))


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def setup(self, screen_dimensions, managers=[]):
        """Setup the particle system with a given screen size."""
        self.screen_dimensions = screen_dimensions
        self.managers = managers

    def create_particles_random(self, number):
        new_particles = []
        for _ in range(number):
            x = random.randint(0, self.screen_dimensions[0])
            y = random.randint(0, self.screen_dimensions[1])
            radius = random.randint(2, 12)
            mass = None #random.uniform(1.0, 10.0)
            density = 1 # random.uniform(0.5, 2.0)
            color = [random.randint(0, 255) for _ in range(3)]
            Particle(x, y, system=self, force_managers=self.managers, radius=radius, mass=mass, density=density, color=color)
            new_particles.append((x, y, radius, mass, density, color))
        return new_particles

    def create_particle(self, x, y, radius=None, mass=None, density=None, color=[random.randint(0, 255) for _ in range(3)]):
        """Create a new particle and add it to the system."""
        if radius is None:
            radius = random.randint(2, 12)
        if density is None:
            density = 1
        return Particle(x, y, system=self, force_managers=self.managers, radius=radius, mass=mass, density=density, color=color)

    def update(self):
        for particle in self.particles:
            particle.update()

    def draw(self, screen):
        for particle in self.particles:
            particle.draw_trail(screen)
            particle.draw_dot(screen)

    def print_info(self):
        for particle in self.particles:
            print(f"Particle of color {particle.color} at {particle.position}, velocity: {particle.velocity}, mass: {particle.mass}, radius: {particle.radius}, density: {particle.density}")
    
    def clear(self):
        self.particles.clear()
    
    def remove_particle(self, particle_id):
        if -len(self.particles) <= particle_id < len(self.particles):
            del self.particles[particle_id]
        else:
            raise IndexError("Particle ID out of range.")