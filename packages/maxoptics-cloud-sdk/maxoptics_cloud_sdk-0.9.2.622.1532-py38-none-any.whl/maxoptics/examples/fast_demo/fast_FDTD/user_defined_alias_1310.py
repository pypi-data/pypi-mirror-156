from copy import deepcopy
from pathlib import Path

import maxoptics.maxopt_sdk as sdk
from maxoptics.maxopt_sdk import FDTD, EME
from maxoptics.maxopt_sdk import View

# ----------- Set materical
sdk.init_materials('./user_defined_materials_1310.json')
Si = sdk.Material.find('Si')
SiO2 = sdk.Material.find('SiO2')
Air = sdk.Material.find('Air')
SiN = sdk.Material.find('SiN')


class EmptyClass:
    ...


fdtd_config = {
    'x': 0,
    'y': 0,
    'z': 0,
    'x_span': 11,
    'y_span': 12,
    'z_span': 8,
    'background_material': SiO2,
    'simulation_time': 10000,  # default 1000fs
    'mesh_type': 0,            # set FDTD mesh_type [0:Auto non-uniform, 1:Uniform]
    'cells_per_wavelength': 6,  # set FDTD's cells_per_wavelength = 2 + LumMesh*4
    'refinement_type': 1,
    # set FDTD's refinement_type [0:Staircase, 1:Average volume average, 2:Dielectric volume average, 4:CP-EP]
    'grading_factor': 1.2,     # higher factor brings wider grids at low index material, typical 1.2
    'x_min_bc': 0,             # set FDTD's xyz boundary conditions [0:PML, 1:PEC]
    'x_max_bc': 0,             # set FDTD's xyz boundary conditions [0:PML, 1:PEC]
    'y_min_bc': 0,             # set FDTD's xyz boundary conditions [0:PML, 1:PEC]
    'y_max_bc': 0,             # set FDTD's xyz boundary conditions [0:PML, 1:PEC]
    'z_min_bc': 0,             # set FDTD's xyz boundary conditions [0:PML, 1:PEC]
    'z_max_bc': 0,             # set FDTD's xyz boundary conditions [0:PML, 1:PEC]
}


def view_index_fdtd(project, fdtd_config, view_axis, view_location, x_span, y_span, z_span):
    fdtd_config_view = deepcopy(fdtd_config)
    fdtd_config_view.update({view_axis: view_location, view_axis + '_span': 0.4,
                            'z_span': z_span, 'x_span': x_span, 'y_span': y_span})
    fdtd_view = FDTD(fdtd_config_view)
    fdtd_view.set_geometry(**fdtd_config_view)
    fdtd_view.add_structure(project.structures)
    result = fdtd_view.run_meshgen()
    view = View(Path(result.workspace) / "mesh.mesh", fdtd_view)
    if view_axis == 'x':
        # show=True jump not save, show=false no jump but save
        view.plot2D(grid='off', show=True, x=fdtd_config_view[view_axis])
    if view_axis == 'y':
        view.plot2D(grid='off', show=False, y=fdtd_config_view[view_axis])
    if view_axis == 'z':
        view.plot2D(grid='off', show=False, z=fdtd_config_view[view_axis])


def view_index_eme(project, eme_config, view_axis, view_location, x_span, y_span, z_span):
    eme_config_view = deepcopy(eme_config)
    eme_config_view.update({view_axis: view_location, view_axis + '_span': 0.4,
                           'z_span': z_span, 'x_span': x_span, 'y_span': y_span})
    eme_view = EME(eme_config_view)
    eme_view.set_geometry(**eme_config_view)
    eme_view.add('EMEPort')   # need to be removed in version v0.0.9
    eme_view.add_structure(project.structures)
    result = eme_view.run_meshgen()
    view = View(Path(result.workspace) / "mesh.mesh", eme_view)
    if view_axis == 'x':
        # show=True jump not save, show=false no jump but save
        view.plot2D(grid='off', show=False, x=eme_config_view[view_axis])
    if view_axis == 'y':
        view.plot2D(grid='off', show=False, y=eme_config_view[view_axis])
    if view_axis == 'z':
        view.plot2D(grid='off', show=False, z=eme_config_view[view_axis])


source_config = {
    'x': 0,
    'y': 0,
    'z': 0,
    'x_span': 0,
    'y_span': 0,
    'z_span': 0,
    'x_min_bc': 1,  # [0:PML, 1:PEC, 2:PMC, 3:Symmetric, 4:Anti-Symmetry, 5:Periodic]
    'x_max_bc': 1,  # [0:PML, 1:PEC, 2:PMC, 5:Periodic]
    'y_min_bc': 1,  # [0:PML, 1:PEC, 2:PMC, 3:Symmetric, 4:Anti-Symmetry, 5:Periodic]
    'y_max_bc': 1,  # [0:PML, 1:PEC, 2:PMC, 5:Periodic]
    'z_min_bc': 1,  # [0:PML, 1:PEC, 2:PMC, 3:Symmetric, 4:Anti-Symmetry, 5:Periodic]
    'z_max_bc': 1,  # [0:PML, 1:PEC, 2:PMC, 5:Periodic]
    'injection_axis': 0,  # set ModeSource's injection_axis param [0:x-axis, 1:y-axis ,2:z-axis ]
    'direction': 0,       # set ModeSource's direction param [0:Forward, 1:Backward]
    # set ModeSource's mode_selection [0:fundamental mode, 1:fundamental TE mode, 2:fundamental TM mode, 3:user select]
    'mode_selection': 0,
    # mode_index calculatored in mode_selection which rank by refractive index.
    # You don't have to write this when mode_selection is not 'user select'
    # 'mode_index': 1,
    'number_of_trial_modes': 5,      # set number of trial modes
}

eme_config = {
    'background_material': SiO2,
    'use_wavelength_sweep': 1,
    'wavelength': 1.31,
    'define_y_mesh': 1,  # boolean parameter. 1 allow to set dy.
    'define_z_mesh': 1,
    'dy': 0.02,  # um
    'dz': 0.02,  # um
    'min_mesh_step': 1e-5,  # um
    'grading_factor': 1.2,
    'refinement_type': 1,   # 1:Dielectric volume average
    'grading_factor': 1.2,
    'y_min_bc': 0,  # [0:PML, 1:PEC, 2:PMC, 3:Symmetric, 4:Anti-Symmetry, 5:Periodic]
    'y_max_bc': 0,  # [0:PML, 1:PEC, 2:PMC, 5:Periodic]
    'z_min_bc': 0,  # [0:PML, 1:PEC, 2:PMC, 3:Symmetric, 4:Anti-Symmetry, 5:Periodic]
    'z_max_bc': 0,  # [0:PML, 1:PEC, 2:PMC, 5:Periodic]
}
