## Supplementary files for: 
# "OTSun, a Python package for the optical analysis of solar-thermal collectors and photovoltaic cells with arbitrary geometry"
## By Gabriel Cardona and Ramon Pujol

The requirements to run these scripts are python 3.6 with the library `otsun` installed (can be installed via `pip`), together with the FreeCAD libray. For convenience of the reader, a `Vagrantfile` is provided, which together with `bootstrap.sh` can be used by [vagrant](https://www.vagrantup.com/) to create a virtual machine with all the requirements installed.

The included files and folders are:

* `validation1.py`: Script used to make the computations for the first validation of OTSun in the main paper.
* `LFR_Focus.FCStd`: FreeCAD file defining the geometry of the optical system used in `validation1.py`.
* `LFR_constant_materials.tnh`: Tonatiuh file defining the same geometry as in `LFR_Focus.FCStd`
* `validation2.py`: Script used to make the computations for the second validation of OTSun in the main paper.
* `Glass_Box_Metallic_Coating.FCStd`: FreeCAD file defining the geometry of the optical system used in `validation2.py`.
* `data`: Folder with data for specification of parametric materials and solar spectrum.

To reproduce the computations, simply run the scripts `validation1.py` and `validation2.py`. The results will be found in the created folders `output1` and `output2`, respectively.
