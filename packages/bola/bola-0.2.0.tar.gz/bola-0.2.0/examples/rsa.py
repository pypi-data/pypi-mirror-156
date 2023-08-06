from bola.psd import GradingCurves, sample_grading_curve
from bola.packing import rsa
from bola.visu import show
import numpy as np


def polydisperse():
    L = 50.0
    phi = 0.6

    gc = GradingCurves.fuller(d_min=0.5)
    radii = sample_grading_curve(gc, L ** 3 * phi)
    spheres = rsa(radii, (L, L, L))

    show(spheres, (L, L, L))


def monodisperse():
    N, R, L = 1000, 0.1, 3
    radii = np.full(N, R)
    spheres = rsa(radii, (L, L, L))
    show(spheres, (L, L, L))


if __name__ == "__main__":
    monodisperse()
    polydisperse()
