
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import Celestcoord.InNCon as IN
import math


def Plot():
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    u=np.linspace(0,np.pi,100)
    v=np.linspace(0,2*np.pi,100)
    r=1
    #Converting r,u,v to Cartesian Co-ordinates
    x=r* np.outer(np.cos(u), np.sin(v))
    y=r* np.outer(np.sin(u), np.sin(v))
    z=r*np.outer(np.ones(np.size(u)), np.cos(v))
    #Plotting a wireframe Celestial Sphere
    plot1=ax.plot_wireframe(x,y,z,rstride=5,cstride=5,label="Celestial Sphere")

    zcircle=0*np.outer(np.ones(np.size(u)), np.ones(np.size(v)))
    PL=ax.plot_surface(x,y,zcircle,rstride=5,cstride=5,color="yellow",label="Equtorial Plane")
    PL._edgecolors2d = PL._edgecolors3d
    PL._facecolors2d = PL._facecolors3d

    #Plotting a vector for Vernal Equinox
    class Arrow3D(FancyArrowPatch):

        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            FancyArrowPatch.draw(self, renderer)

    a = Arrow3D([0, 0], [0, 1.5], [0, 0], mutation_scale=20, lw=1, arrowstyle="-|>", color="k")
    ax.add_artist(a)
    #Plotting 
    first_legend = plt.legend(handles=[plot1,PL])
    plt.gca().add_artist(first_legend)
        # legend for vector
    fake2Dline = mpl.lines.Line2D([0],[0], linestyle="none", c='k', marker = 'o',label="Vernal Equinox")
    ax.legend(handles=[fake2Dline],loc='lower left')
    ax.set_xlabel('X', fontsize=20)
    ax.set_ylabel('Y',fontsize=20)
    ax.set_zlabel('Z',fontsize=20)
    ax.invert_xaxis()
    #Plotting the RA and Dec Values
    error=None
    try:
        RA,Dec=IN.In() 
        RA_deg,Dec_deg=IN.Convert(RA,Dec)
        class ValError(Exception):
            pass
        if( math.isnan(RA_deg)==True and math.isnan(Dec_deg)==True):
            raise ValError
        x_deg=math.cos(math.radians(RA_deg))*math.cos(math.radians(Dec_deg))
        y_deg=math.sin(math.radians(RA_deg))*math.cos(math.radians(Dec_deg))
        z_deg=math.sin(math.radians(Dec_deg))
        ax.scatter([x_deg],[y_deg],[z_deg],color="r")
        plt.show()
    except ValError:
        print("CelSphere.py says: RA and Dec Values are empty")
  
if __name__ == '__main__':
    Plot()