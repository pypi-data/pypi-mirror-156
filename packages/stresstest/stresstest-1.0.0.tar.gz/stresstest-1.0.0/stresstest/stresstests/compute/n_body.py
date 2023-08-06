import math

from stresstest.stresstest import BaseStresstest, Parameter


class NBodySimulationPurePythonStresstest(BaseStresstest):
    name = ["compute", "n_body", "NBodySimulationPurePythonStresstest"]

    parameters = [Parameter("n_particles", default=1000, type=int)]

    def run_test(self, n_particles: int):
        import random

        particle = []
        for _ in range(n_particles):
            particle.append([random.gauss(0.0, 1.0) for j in range(3)])

        particlev = [[0, 0, 0] for x in particle]

        with self:
            self.nbody(particle, particlev)

    def nbody(self, particle, particlev):
        """Pure-python implementation of the N-body simulation.

        Source: https://hilpisch.com/Continuum_N_Body_Simulation_Numba_27072013.html
        """
        n_particles = len(particle)

        n_steps = 5
        dt = 0.01
        for _ in range(n_steps):
            for i in range(n_particles):
                f_x = 0.0
                f_y = 0.0
                f_z = 0.0
                for j in range(n_particles):
                    if j != i:
                        dx = particle[j][0] - particle[i][0]
                        dy = particle[j][1] - particle[i][1]
                        dz = particle[j][2] - particle[i][2]
                        dr_squared = dx * dx + dy * dy + dz * dz
                        dr_power_n32 = 1.0 / (dr_squared + math.sqrt(dr_squared))
                        f_x += dx * dr_power_n32
                        f_y += dy * dr_power_n32
                        f_z += dz * dr_power_n32
                    particlev[i][0] += dt * f_x
                    particlev[i][1] += dt * f_y
                    particlev[i][2] += dt * f_z
            for i in range(n_particles):
                particle[i][0] += particlev[i][0] * dt
                particle[i][1] += particlev[i][1] * dt
                particle[i][2] += particlev[i][2] * dt
