#
# Script used for second validation of OTSun
#

# ---
# Import libraries
# ---
import otsun
import FreeCAD
from FreeCAD import Base
import numpy as np
from multiprocessing import Pool
import os


# ---
# Single parallelizable computation (fixed angle, polarization and wavelength)
# ---
def single_computation(*args):
    (w, ) = args
    l_s = otsun.LightSource(current_scene, emitting_region, w, 1.0, direction_distribution, polarization_vector)
    exp = otsun.Experiment(current_scene, l_s, number_of_rays)
    exp.run()
    print(f"Computed w={w}, theta={theta}, S/P={sp}")
    return (w, exp.Th_energy, exp.Th_wavelength, exp.captured_energy_Th)


# ---
# Full parallel computation for a fixed angle and polarization
# ---
def full_computation():
    p = Pool(maxtasksperchild=1)
    args_list = [(w,) for w in np.arange(w_ini, w_end + 1E-3, w_step)]
    values = p.starmap(single_computation, args_list)
    p.close()
    p.join()
    print(f"Finished computation w={w_ini}..{w_end}, theta={theta}, S/P={sp}")
    # ---
    # Placeholders to collect data
    # ---
    captured_energy_Th = 0.0
    source_wavelength = []
    Th_energy = []
    Th_wavelength = []
    for value in values:
        (w, exp_Th_energy, exp_Th_wavelength, exp_captured_energy_Th) = value
        Th_energy.append(exp_Th_energy)
        Th_wavelength.append(exp_Th_wavelength)
        source_wavelength.append(w)
        captured_energy_Th += exp_captured_energy_Th

    # ---
    # Save results in file
    # ---
    output_folder = 'output2'
    try:
        os.makedirs(output_folder)
    except:
        pass  # we suppose it already exists

    table_Th = otsun.make_histogram_from_experiment_results(
        Th_wavelength, Th_energy, w_step,
        aperture_collector_Th, emitting_region.aperture
    )
    filename = (f"Th_spectral_efficiency_Glass_BK7_Ag_{int(w_ini)}_{int(w_end)}_{int(theta)}_{sp}.txt")
    np.savetxt(os.path.join(output_folder, filename),
               table_Th, fmt=['%f', '%f'],
               header="#wavelength(nm) efficiency_Th_absorbed")


if __name__ == '__main__':
    # ---
    # Load freecad file
    # ---
    freecad_file = 'mirror.FCStd'
    FreeCAD.openDocument(freecad_file)
    doc = FreeCAD.ActiveDocument

    # ---
    # Definition of materials
    # ---
    otsun.TransparentSimpleLayer("Trans", 1.0)
    otsun.AbsorberSimpleLayer("Abs", 1.0)
    otsun.TwoLayerMaterial("Trans_Abs", "Trans", "Abs")
    file_Glass = os.path.join('data', 'BK7_Schott.txt')
    otsun.WavelengthVolumeMaterial("Glass", file_Glass)
    file_Ag = os.path.join('data', 'Ag_Yang.txt')
    otsun.MetallicSpecularLayer("Ag", file_Ag)
    otsun.ReflectorSpecularLayer("Mirror", 1)

    # ---
    # Definition of parameters for the simulation
    # ---
    # Angles
    phi = 0.0
    thetas = [45.0, 80.0]
    # Wavelengths
    wavelength_ranges = [(300.0, 400.0, 2.0), (420.0, 1000.0, 20.0)]
    # Number of rays to simulate
    number_of_rays = 50000
    # Optical parameters
    aperture_collector_Th = doc.getObject("Trans_Abs").Shape.Faces[0].Area
    direction_distribution = None
    # Scene
    sel = doc.Objects
    current_scene = otsun.Scene(sel)

    # ---
    # Launch computations
    # ---
    for (w_ini, w_end, w_step) in wavelength_ranges:
        for theta in thetas:
            main_direction = otsun.polar_to_cartesian(phi, theta) * -1.0  # Sun direction vector
            emitting_region = otsun.SunWindow(current_scene, main_direction)
            normal = Base.Vector(0, 0, 1)
            s_vector = main_direction.cross(normal)
            p_vector = s_vector.cross(main_direction)
            polarizations = [s_vector, p_vector]
            for (sp, polarization_vector) in zip(['S', 'P'], polarizations):
                full_computation()
