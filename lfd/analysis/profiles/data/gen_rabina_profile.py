import os

import cv2
import numpy as np
import matplotlib.pyplot as plt

from scipy import stats, signal
try:
    from scipy import weave
except:
    pass



my_dpi = 96
xmin, xmax = -6, 6
ymin, ymax = -6, 6
zmin, zmax = -6, 6
N = 1000
theta = 1.6

rangex = (xmin, xmax)
rangey = (ymin, ymax)
rangez = (zmin, zmax)

###############################################
### Rotation matrix and rotation function
###############################################
def rotation_matrix_numpy(axis, theta):
    """Calculates and returns a (3, 3) rotation matrix around the given axis
    (x, y, z) and an angle theta. Slow.
    """
    mat = np.eye(3,3)
    axis = axis/sqrt(np.dot(axis, axis))
    a = cos(theta/2.)
    b, c, d = -axis*sin(theta/2.)

    return np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
                  [2*(b*c+a*d), a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
                  [2*(b*d-a*c), 2*(c*d+a*b), a*a+d*d-b*b-c*c]])


def rotation_matrix_weave(theta, axiss,
                          mat = [1., 0., 0., 0., 1., 0., 0., 0., 1.]):
    """
    *** WEAVE IS DEPRECATED HERE FOR POSTERITY IF EVER CYTHON IMPLEMENTATION
    IS ATTEMPTED ***
    Returns a (3,3) rotation matrix around a given axis (x,y,z) and
    an angle theta.
    Implemented in numpy weave for speed.
    """
    support = "#include <math.h>"
    code = """
        double axis [3] = {axiss[0], axiss[1], axiss[2]};
        double x = sqrt(axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2]);
        double a = cos(theta / 2.0);
        double b = -(axis[0] / x) * sin(theta / 2.0);
        double c = -(axis[1] / x) * sin(theta / 2.0);
        double d = -(axis[2] / x) * sin(theta / 2.0);

        mat[0] = a*a + b*b - c*c - d*d;
        mat[1] = 2 * (b*c - a*d);
        mat[2] = 2 * (b*d + a*c);

        mat[3*1 + 0] = 2*(b*c+a*d);
        mat[3*1 + 1] = a*a+c*c-b*b-d*d;
        mat[3*1 + 2] = 2*(c*d-a*b);

        mat[3*2 + 0] = 2*(b*d-a*c);
        mat[3*2 + 1] = 2*(c*d+a*b);
        mat[3*2 + 2] = a*a+d*d-b*b-c*c;
    """
    weave.inline(code, arg_names=["mat", "axiss", "theta"],
                 support_code = support)

    return np.reshape(mat, (3,3))


def rotate_func_theta(x, y, z, theta, axis=[1.0, 0.0, 0.0]):
    """
    Rotates a function for an angle theta around axis (x,y,z).
    Input x, y, z have to be 2D coordinate arrays where for
    given indices i, j the point coordinates are (x[i,j], y[i,j], z[i,j])
        x, y = np.linspace(...)
        x, y, = np.meshgrid(x,y)
        z = np.zeros(x.shape)
    or
        z = some_function( np.linspace(....) )
        z = np.outer(z,z)
    """
    R = rotation_matrix_weave(theta, axis)

    rx, ry, rz = np.zeros(x.shape), np.zeros(y.shape), np.zeros(z.shape)
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            tmpx, tmpy, tmpz = np.matmul(R, [x[i, j], y[i, j], z[i, j]])
            rx[i,j]+=tmpx
            ry[i,j]+=tmpy
            rz[i,j]+=tmpz
    return rx, ry, rz








###############################################
### Generate plots, convenience
###############################################
def rotate_2Dgaus_range(x, y, z, thetamin, thetamax, my_dpi, Npoints, step=0.1,
                      Nlevels=1000, axis=[1.0, 0.0, 0.0]):
    """
    Rotates a gaussian function for series of angles [thetamin, thetamax> and
    calculates its projection onto a background plane.
    """
    angles = np.arange(thetamin, thetamax, step)
    nangl = len(angles)
    for i in angles:
        rx, ry, rz = rotate_func_theta(x, y, z, i)
        rx2, ry2, rz2 = rotate_func_theta(xp, yp, zp, i)

        rx, ry, rz = rx+5.0, ry+5.0, rz+5.0
        rx2, ry2, rz2 = rx2+5.0, ry2+5.0, rz2+5.0

        leveled = rz-rz2
        levs = np.linspace(leveled.min(), leveled.max(), 1000)

        fig = plt.figure(figsize=(Npoints/float(my_dpi),
                                  Npoints/float(my_dpi)), dpi=my_dpi)
        fig.subplots_adjust(bottom=0., left=0., right=1., top=1.)
        ax = fig.add_subplot(111)
        ax.contourf(rx, ry, leveled, levs, cmap="gray_r")

        plt.savefig('Rabina/img{0}_r.png'.format(int(i*10)),dpi=my_dpi)
        #plt.show()
        plt.cla()
        plt.clf()
        plt.close()



def rotate_Rabina_range(x, y, z, thetamin, thetamax, my_dpi, Npoints, step=0.1,
                      Nlevels=1000, axis=[1.0, 0.0, 0.0]):
    """
    Rotates a function for series of angles [thetamin, thetamax>. Rotating a 2D
    function means, essentially, to map a new set of coordinates (x, y) to the
    function value at the old coordinates f(x', y').

    Rotating a 3D distriution means mapping to a new set of coordinates (x,y,z)
    the distribution probability value at the old coordinates f(x', y', z').
    The proper way to do this would be to generate the probability distribution
    and then ray-trace through it accumulating values to project on the
    background plane.

    This is done here via an approximative work-around where instead of ray
    tracing through the distribution a set of planes are generated in the range
    [zmin, zmax]. These planes are then rotated around an axis for angle theta.
    New probabilities are calculated for each of the generated planes and then
    all planes are summed into a final projection.
    """
    #angles = np.arange(thetamin, thetamax, step)
    #nangl = len(angles)
    angles = [0.0, 0.523599, np.pi/2.0001]

    for i in angles:
        rx, ry, rz = rotate_func_theta(x, y, z, i, axis=[0.0, 1.0, 0.0])
        w = gen_Rabina(rx, ry, rz)
        normed = w/w.max()
        normed *= 255.0
        normed += 1.0
        levs = np.linspace(normed.min(), normed.max(), 1000)

        fig = plt.figure(figsize=(Npoints/float(my_dpi),
                                  Npoints/float(my_dpi)), dpi=my_dpi)
        fig.subplots_adjust(bottom=0., left=0., right=1., top=1.)
        ax = fig.add_subplot(111)

        # Consider avoiding contourf and using pcolormesh instead?
        ax.contourf(rx, ry, normed, levs, cmap="gray_r")

        #normed = w/w.max()

        #ax.plot_surface(rx, ry, normed, color='red',alpha=0.65, linewidth=1)

        plt.savefig('Rabina/img{0}_r.png'.format(int(i*10)),dpi=my_dpi)
        #plt.show()
        plt.cla()
        plt.clf()
        plt.close()
        #break



###############################################
### Generate Distributions
###############################################
def get_2Dgaus(rangex, rangey, N):
    xmin, xmax = rangex
    ymin, ymag = rangey
    x = np.linspace(xmin, xmax, N)
    y = np.linspace(ymin, ymax, N)
    z = stats.multivariate_normal().pdf(x)
    x, y = np.meshgrid(x, y)
    z = np.outer(z, z)
    z = z*1/z.max()
    return x, y, z

def get_zero_plane(xminmax, yminmax, N):
    xmin, xmax = xminmax
    ymin, ymax = yminmax
    x = np.linspace(xmin, xmax, N)
    y = np.linspace(ymin, ymax, N)
    x, y = np.meshgrid(x, y)
    return x, y, np.zeros(x.shape)

def F(x, u, r, l):
	xx = x.copy()
	xx[x<u] = np.exp((x[x<u]-u)/l)
	xx[(x >= u) & (x <= u+r)] = 1 - np.power(x[(x >= u) & (x <= u+r)] - u , 2.0)/(r*r)
	xx[x>u+r] = 0.0
	return xx

def gen_Rabina(x, y, z, r=0.6, k=0.15, l=3, u=4):
	fx = F(x, u=u, r=r, l=l)

	midbottmp = r + k * (u - x)
	midbot = midbottmp*midbottmp
	mid = (r*r)/midbot
	right = np.exp( -1 * (y*y + z*z) / midbot )

	return 2*np.pi*fx*mid*right

###############################################
### The plot
###############################################
x = np.linspace(xmin, xmax, N)
y = np.linspace(ymin, ymax, N)
x, y = np.meshgrid(x, y)

wtot = np.zeros(x.shape)
z = np.zeros(x.shape)



rotate_Rabina_range(x, y, z, thetamin=0.0, thetamax=np.pi/2.0001,
                    my_dpi=my_dpi, Npoints=N)
