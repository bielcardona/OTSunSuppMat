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
    wavelengths = np.arange(wavelength_ini, wavelength_end + 1E-4, wavelength_step)
    args_list = [(w,) for w in wavelengths]
    values = p.starmap(single_computation, args_list)
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
        Th_wavelength, Th_energy, wavelength_step,
        aperture_collector_Th, emitting_region.aperture
    )
    filename = (f"Th_spectral_efficiency_Glass_BK7_Ag_"
                f"{theta}_{sp}_{wavelength_ini}_{wavelength_end}_{number_of_rays}_rays.txt")
    np.savetxt(os.path.join(output_folder, filename),
               table_Th, fmt=['%f', '%f'],
               header="#wavelength(nm) efficiency_Th_absorbed")


if __name__ == '__main__':
    # ---
    # Load freecad file
    # ---
    freecad_file = 'Glass_Box_Metallic_Coating.FCStd'
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
    wavelength_ini = 300.0
    wavelength_end = 400.0
    wavelength_step = 2.0
    # Number of rays to simulate
    number_of_rays = 50# 000
    # Optical parameters
    aperture_collector_Th = doc.getObject("Trans_Abs").Shape.Faces[0].Area
    direction_distribution = None
    internal_quantum_efficiency = 1.0
    # Scene
    sel = doc.Objects
    current_scene = otsun.Scene(sel)

    # ---
    # Launch computations
    # ---
    for theta in thetas:
        main_direction = otsun.polar_to_cartesian(phi, theta) * -1.0  # Sun direction vector
        emitting_region = otsun.SunWindow(current_scene, main_direction)
        normal = Base.Vector(0, 0, 1)
        s_vector = main_direction.cross(normal)
        p_vector = s_vector.cross(main_direction)
        polarizations = [s_vector, p_vector]
        for (sp, polarization_vector) in zip(['S', 'P'], polarizations):
            full_computation()
