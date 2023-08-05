import glob
import json
from matplotlib import pyplot as plt
import os
from pathlib import Path
import time

import numpy as np
from importlib.resources import path
from maxoptics.core import lineplot, plot
import maxoptics.maxopt_sdk as sdk
from maxoptics.maxopt_sdk import (
    FDTD,
    TaskResult,
    passive_fdtd_fd_result_chart,
    passive_source_fde_result_chart,
    passive_fdtd_mode_expansion_chart,
    passive_fdtd_mode_expansion_fde_result_chart,
)
import seaborn

from user_defined_alias_1310 import Si, SiO2, fdtd_config, source_config, view_index_fdtd, EmptyClass


def simulation(
        gds_file,
        gds_topcell,
        project_address,
        run=False,
        source_view=False,
        extract=False,
        grids_per_lambda=6):
    # -------general parameter
    monitor_w = 2.0
    monitor_h = 2.0
    port_files = glob.glob(os.path.join(path, 'port*.json'))
    if len(port_files) > 0:
        with open(port_files[0]) as json_file:
            ports = json.load(json_file)
    plot_path = str(Path(__file__).parent.as_posix()) + '/plots/fdtdfast/'
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    # -----------1 FDTD config
    fdtd_config_private = {
        'x'                   : 0,
        'y'                   : 0,
        'z'                   : 0,
        'x_span'              : 6,
        'y_span'              : monitor_w,
        'z_span'              : monitor_h,
        'cells_per_wavelength': grids_per_lambda,
        'name'                : 'fast_FDTD'
    }
    fdtd_config.update(fdtd_config_private)
    fdtd = FDTD(fdtd_config)
    fdtd.set_geometry(**fdtd_config)

    # --------2.set project and structure     -----------------
    project = sdk.GdsModel(gds_file)
    # add rectangle((center_x,center_y),x_span,y_span,rotation_angle,z_min,z_max,material)
    project.add_rectangle((0, 0), 6, monitor_w, 0, -0.1, 0.1, Si)
    project.gds_import(gds_topcell, (3, 0), SiO2, 0, 0.1)                         # si dwg etch
    # view_index_fdtd(
    #     project=project,
    #     fdtd_config=fdtd_config,
    #     view_axis='x',
    #     view_location=ports['op_0']['position'][0],
    #     z_span=monitor_h,
    #     y_span=monitor_w,
    #     x_span=0.2)  # source
    # view_index_fdtd(
    #     project=project,
    #     fdtd_config=fdtd_config,
    #     view_axis='x',
    #     view_location=ports['op_1']['position'][0],
    #     z_span=monitor_h,
    #     y_span=monitor_w, x_span=0.2)  # monitorT
    fdtd.add_structure(project.structures)

    # --------3.set waveform and source     -----------------
    sdk.init_waveforms('./user_defined_waveforms_1310.json')
    waveform = sdk.Waveform.find('Waveform_1310_100')
    source_config_private = {
        'x'             : ports['op_0']['position'][0],
        'y'             : ports['op_0']['position'][1],
        'z'             : 0,
        'x_span'        : 0,
        'y_span'        : monitor_w,
        'z_span'        : monitor_h,
        'mode_selection': 3
    }
    source_config.update(source_config_private)
    source_config["waveform_id"] = waveform.id
    src = fdtd.add("ModeSource", source_config)
    src.set_geometry(**source_config)
    fdtd.add("GlobalMonitor", {
        "frequency_points" : 201,
        "wavelength_center": waveform.data['center_wavelength'],
        "wavelength_span"  : waveform.data['wavelength_span']})
    fdtd.update(waveforms=[waveform])

    # --------4.set monitor    -----------------------------------
    fdtd.add("TimeMonitor")
    z_normal = {
        'x'                     : fdtd_config["x"],
        'y'                     : fdtd_config["y"],
        'z'                     : fdtd_config["z"],
        'x_span'                : fdtd_config["x_span"],
        'y_span'                : fdtd_config["y_span"],
        'z_span'                : 0,
        'use_wavelength_spacing': 1,  # use wavelength_spacing [1:on, 0:off]
        'use_source_limits'     : 0,  # source_limits [1:on, 0:off]
        'frequency_points'      : 3,
        "wavelength_center"     : waveform.data['center_wavelength'],
        "wavelength_span"       : waveform.data['wavelength_span'],
        "spacing_type"          : 0,   # [0:wavelength, 1:frequency]
        "spacing_limit"         : 0    # [0:min/max, 1:center/span]
    }

    monitor_T = {
        'x'                     : ports['op_1']['position'][0],
        'y'                     : ports['op_1']['position'][1],
        'z'                     : 0,
        'x_span'                : 0,
        'y_span'                : monitor_w,
        'z_span'                : monitor_h,
        'use_wavelength_spacing': 1,  # use wavelength_spacing [1:on, 0:off]
        'use_source_limits'     : 0,  # source_limits [1:on, 0:off]
        "spacing_type"          : 0,  # [0:wavelength, 1:frequency]
        "spacing_limit"         : 0,  # [0:min/max, 1:center/span]
        "mode_expansion": {
            "on"       : True,
            "x"        : ports['op_1']['position'][0],
            "y"        : ports['op_1']['position'][1],
            "z"        : 0,
            "x_span"   : 0,
            "y_span"   : monitor_w,
            "z_span"   : monitor_h,
            "mode_list": [1, 2, 3, 4],
        }
    }

    monitor_R = {
        'x'                     : ports['op_0']['position'][0] - 1,
        'y'                     : ports['op_0']['position'][1],
        'z'                     : 0,
        'x_span'                : 0,
        'y_span'                : monitor_w,
        'z_span'                : monitor_h,
        'use_wavelength_spacing': 1,  # use wavelength_spacing [1:on, 0:off]
        'use_source_limits'     : 0,  # source_limits [1:on, 0:off]
        "spacing_type"          : 0,  # [0:wavelength, 1:frequency]
        "spacing_limit"         : 0   # [0:min/max, 1:center/span]
    }

    z_normal_mon = fdtd.add("PowerMonitor", z_normal)
    z_normal_mon.set_geometry(**z_normal)

    monitor_T_mon = fdtd.add("PowerMonitor", monitor_T)
    monitor_T_mon.set_geometry(**monitor_T)

    monitor_R_mon = fdtd.add("PowerMonitor", monitor_R)
    monitor_R_mon.set_geometry(**monitor_R)

    project.show(savepath=Path(plot_path), show=False)
    if run:
        start = time.time()
        print('\x1b[6;30;42m' + '-------starting FDTD now !!!!------------- ' + '\x1b[0m')
        result = fdtd.run()
        fdtd.run_mode_expansion(fdtd_path=result.workspace)             # for mode monitor
        print('\x1b[6;30;42m' + '[Finished in %(t)s mins for FDTD]' %
              {'t': round((time.time() - start) / 60, 2)} + '\x1b[0m')

    if source_view:
        # =============   jpg mode source, now only after FDTD
        result = fdtd.run(only_fde=True)
        df = passive_source_fde_result_chart(
            "intensity",
            dict(
                monitor=src,
                attribute="E",
                operation="ABS",
                taskPath=Path(
                    result.workspace).parent
                / Path(
                    result.workspace).name,
            ),
            dict(
                x=0,
                y="plotX",
                z="plotY",
                mode=0),
        )
        tf = TaskResult(df, "intensity")
        x, y, Z = tf.raw_data["horizontal"], tf.raw_data["vertical"], tf.raw_data["data"]
        sdk.heatmap(x, y, Z)
        plt.xlabel("x (μm)")
        plt.ylabel("y (μm)")
        plt.title("source_mode_profile")
        plt.savefig(plot_path + "00_source_modeprofile_fdeonly.jpg")
        plt.clf()
        print('=========================== generated source profile from FDE-only =================================')

    if extract:
        # =============   see results from FDTD
        if not run:
            result = EmptyClass()
            result.workspace = project_address                                          # for power monitor
        me_result = fdtd.run_mode_expansion(fdtd_path=result.workspace)             # for mode monitor

        # ========================   see mode profile at output ports
        df = passive_fdtd_mode_expansion_fde_result_chart(
            "intensity",
            dict(
                log=False,
                monitor=monitor_T_mon,
                attribute="E",
                operation="Real",
                taskPath=Path(me_result.workspace)), 
            dict(
                x=0,
                y='plotX',
                z='plotY',
                mode="1"),
        )
        tf = TaskResult(df, "intensity")
        x, y, Z = tf.raw_data["horizontal"], tf.raw_data["vertical"], tf.raw_data["data"]
        sdk.heatmap(x, y, Z)
        plt.xlabel("x (μm)")
        plt.ylabel("y (μm)")
        plt.title("mode=1 profile")
        plt.savefig(plot_path + "01_monitorT_modeprofile_fdtd.jpg")
        plt.clf()

        # =============   jpg top view, power monitor
        df = passive_fdtd_fd_result_chart(
            "intensity",
            dict(
                log=False,
                monitor=z_normal_mon,
                attribute="E",
                operation="ABS",
                taskPath=Path(
                    result.workspace).parent
                / Path(
                    result.workspace).name),
            dict(
                x="plotX",
                y="plotY",
                z=0,
                wavelength=0),
        )
        tf = TaskResult(df, "intensity")
        x, y, Z = tf.raw_data["horizontal"], tf.raw_data["vertical"], tf.raw_data["data"]
        sdk.heatmap(x, y, Z)
        plt.xlabel("x (μm)")
        plt.ylabel("y (μm)")
        plt.title("z_normal_mon-E-ABS-x-y heatmap with z=0")
        plt.savefig(plot_path + "02_top_profile.jpg")
        plt.clf()

        # ========================   jpg Transmission, power monitor
        df = passive_fdtd_fd_result_chart(
            "line",
            dict(log=False, monitor=monitor_T_mon, attribute="T", operation="Real", taskPath=Path(result.workspace)),
            dict(x=0, y=0, z=0, wavelength="plotX"),
        )
        tf = TaskResult(df, "line")
        # --------
        seaborn.lineplot(x=tf.DataFrame.index, y=10 * np.log10(tf.DataFrame['data'].values), markers=True)
        plt.xlabel("wavelength (μm)")
        plt.ylabel("Transmission_Through")
        plt.ylim(-0.2, 0.1)
        plt.title(plot_path + "03_Trans_ThroughVsLambda_power.jpg")
        plt.savefig(plot_path + "03_TransVsLambda_power.jpg")
        plt.clf()

        # # ========================   mode monitor, x: wavelength, y:Trans
        df = passive_fdtd_mode_expansion_chart(
            "line",
            dict(
                log=False,
                monitor=monitor_T_mon,
                attribute="t_forward",
                operation="ABS",
                taskPath=Path(
                    me_result.workspace)),
            dict(
                mode="1",
                wavelength="plotX"))
        tf = TaskResult(df, "line")
        # --------
        seaborn.lineplot(data=tf.DataFrame)
        plt.xlabel("wavelength (μm)")
        plt.ylabel("intensity")
        # plt.ylim(-5, 0.1)
        plt.title("mode=1_line_plot")
        plt.savefig(plot_path + "04_TransVsLambda_mode=1.jpg")
        plt.clf()

        # ========================   mode monitor, x: mode order, y:Trans. to check light leaking to higher order mode
        df = passive_fdtd_mode_expansion_chart(
            "line",
            dict(
                log=False,
                monitor=monitor_T_mon,
                attribute="t_forward",
                operation="ABS",
                taskPath=Path(
                    me_result.workspace),
            ),
            dict(
                mode="plotX",
                wavelength="1.31"))
        tf = TaskResult(df, "line")
        seaborn.lineplot(data=tf.DataFrame)
        plt.xlabel("mode num")
        plt.ylabel("Transmission Forward")
        plt.title(plot_path + "Trans_by_ModeOrder")
        plt.savefig(plot_path + "05_TransVsOrder.jpg")
        plt.clf()
        print('============ Trans_by_mode ====================')

        # ========================   jpg Return loss, power monitor
        df = passive_fdtd_fd_result_chart(
            "line",
            dict(log=False, monitor=monitor_R_mon, attribute="T", operation="Real", taskPath=Path(result.workspace)),
            dict(x=0, y=0, z=0, wavelength="plotX"),
        )
        tf = TaskResult(df, "line")
        # ---------
        seaborn.lineplot(x=tf.DataFrame.index, y=10 * np.log10(-tf.DataFrame['data'].values), markers=True)
        plt.xlabel("wavelength (μm)")
        plt.ylabel("Return loss (dB)")
        plt.title(plot_path + "Rel_mon Real(T) line")
        plt.ylim(-100, 0.1)
        plt.savefig(plot_path + "06_RlVsLambda_power.jpg")
        plt.clf()


if __name__ == '__main__':
    start = time.time()
    path = str(Path(__file__).parent.as_posix())
    gds_file = path + '/' + 'fast_fdtd.gds'
    project_address = path + '/project/'
    simulation(
        extract=True,
        source_view=False,
        run=True,
        gds_file=gds_file,
        gds_topcell="EXTEND_1",
        grids_per_lambda=10,
        project_address=project_address
    )
    print('\x1b[6;30;42m' + '[Finished in %(t)s mins]' % {'t': round((time.time() - start) / 60, 2)} + '\x1b[0m')
