import matplotlib.pyplot as plt
import numpy as np

def show_particles(self, level=None,
    full_sim=False):

    if level is None:
        level = self.current_level

    prev_level = self.current_level
    # gets the info on the level requested
    self.set_level(level)

    # dark mode for cool kids B-) 
    plt.style.use('dark_background')

    # load the particle data
    id, xi, yi, zi = np.genfromtxt(self.initial_particle_file, unpack=True)
    id, xf, yf, zf = np.genfromtxt(self.final_particle_file, unpack=True)

    xi *= self.box_length
    yi *= self.box_length
    zi *= self.box_length

    xf *= self.box_length
    yf *= self.box_length
    zf *= self.box_length
    

    # create the figure
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(projection='3d')

    ax.scatter(xi,yi,zi, c='red')
    ax.scatter(xf,yf,zf, c='blue')

    ax.set_xlabel('x (Mpc/h)')
    ax.set_ylabel('y (Mpc/h)')
    ax.set_zlabel('z (Mpc/h)')

    if (full_sim):

        ax.set_xlim(0, self.box_length)
        ax.set_ylim(0, self.box_length)
        ax.set_zlim(0, self.box_length)

    else :
        ax.set_xlim(min(xi), max(xi))
        ax.set_ylim(min(yi), max(yi))
        ax.set_zlim(min(zi), max(zi))

    plt.show()

    # reset this to reduce statefulness
    self.set_level(prev_level)
