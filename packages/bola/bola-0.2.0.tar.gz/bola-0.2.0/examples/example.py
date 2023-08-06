from pathlib import Path

import numpy as np

from bola import psd
from bola import packing
from bola import mesh
from bola import visu


def main():
    out = Path(__file__).resolve().parent

    gc = psd.GradingCurves.fuller(4.0, 16.0, 0.5)
    box = (32.0, 32.0, 32.0)
    radii = psd.sample_grading_curve(gc, V=0.5 * np.prod(box))

    spheres = packing.rsa(radii, box)

    growth_rate = 0.1
    sim = packing.edmd(box, spheres, growth_rate=growth_rate)
    visu.show(radii, filename=out / "gc.jpg")
    visu.show(spheres, box, filename=out / "rsa.jpg")

    t_max = 10.0
    while sim.t() < t_max:
        sim.process(100 * len(radii))
        sim.synchronize(True)
        print(packing.stats_string(sim), flush=True)

    new_spheres = sim.spheres()
    new_spheres[:, 3] = radii

    visu.show(new_spheres, box, filename=out / "edmd.jpg")

    mesh.create(
        box,
        new_spheres,
        mesh.GmshOptions(
            mesh_size_matrix=2, mesh_size_aggregates=2, out=out / "mesh.xdmf"
        ),
    )


if __name__ == "__main__":
    main()
