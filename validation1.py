#
# Script used for first validation of OTSun
#

# ---
# Import libraries
# ---
import otsun
import os
import FreeCAD
import numpy as np
from multiprocessing import Pool


# ---
# Single parallelizable computation (fixed angles)
# ---
def single_computation(*args):
    (ph, th) = args
    main_direction = otsun.polar_to_cartesian(ph, th) * -1.0  # Sun direction vector
    current_scene = otsun.Scene(sel)
    tracking = otsun.MultiTracking(main_direction, current_scene)
    tracking.make_movements()
    emitting_region = otsun.SunWindow(current_scene, main_direction)
    l_s = otsun.LightSource(current_scene, emitting_region, light_spectrum, 1.0, direction_distribution)
    exp = otsun.Experiment(current_scene, l_s, number_of_rays, None)
    exp.run()
    tracking.undo_movements()
    print(f"Computed ph={ph}, th={th}")
    efficiency_from_source_Th = (exp.captured_energy_Th / aperture_collector_Th) / (
        exp.number_of_rays / exp.light_source.emitting_region.aperture)
    return ph, th, efficiency_from_source_Th


# ---
# Full parallel computation
# ---
def full_computation(ph):
    p = Pool(maxtasksperchild=1)
    args_list = [(ph, th) for th in np.arange(theta_ini, theta_end, theta_step)]
    values = p.starmap(single_computation, args_list)

    # ---
    # Save results in file
    # ---
    output_folder = 'output1'
    output_file = os.path.join(output_folder, f'efficiency_results_{int(ph)}.txt')
    try:
        os.makedirs(output_folder)
    except:
        pass  # we suppose it already exists

    with open(output_file, 'w') as f:
        f.write(f"{aperture_collector_Th * 1E-6} # Collector Th aperture in m2\n")
        f.write(f"{power_emitted_by_m2} # Source power emitted by m2\n")
        f.write(f"{number_of_rays} # Rays emitted per sun position\n")
        f.write("# phi theta efficiency_from_source_Th\n")
        for value in values:
            (ph, th, efficiency_from_source_Th) = value
            f.write(f"{ph:.3f} {th:.3f} {efficiency_from_source_Th:.6f}\n")


if __name__ == '__main__':
    # ---
    # Load freecad file
    # ---
    freecad_file = 'LFR.FCStd'
    FreeCAD.openDocument(freecad_file)
    doc = FreeCAD.ActiveDocument

    # ---
    # Definition of materials
    # ---
    otsun.ReflectorSpecularLayer("Mir1", 0.95)
    otsun.ReflectorSpecularLayer("Mir2", 0.91)
    otsun.AbsorberSimpleLayer("Abs", 0.95)
    otsun.TransparentSimpleLayer("Trans", 0.965)
    otsun.OpaqueSimpleLayer("Opa")

    # ---
    # Definition of parameters for the simulation
    # ---
    # Angles
    phi_ini = 0.0
    phi_end = 90.0
    phi_end = phi_end + 1.E-4
    phi_step = 90.0
    theta_ini = 0.0
    theta_end = 90.0
    theta_end = theta_end + 1.E-4
    theta_step = 5.0
    # Number of rays to simulate
    number_of_rays = 100# 000
    # Optical parameters
    aperture_collector_Th = 11 * 0.5 * 32 * 1000000
    CSR = 0.05
    direction_distribution = otsun.buie_distribution(CSR)
    data_file_spectrum = os.path.join('data', 'ASTMG173-direct.txt')
    light_spectrum = otsun.cdf_from_pdf_file(data_file_spectrum)
    power_emitted_by_m2 = otsun.integral_from_data_file(data_file_spectrum)
    # Scene
    sel = doc.Objects

    # ---
    # Launch computations
    # ---
    for ph in np.arange(phi_ini, phi_end,  phi_step):
        full_computation(ph)
