from src import Q_
from src.systems import *
from src.load_config import get_vehicles
from src.optimization import Constraint

from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.io import save,output_file

def save_original_states(vehicle:Vehicle,params:list[str]):
    save_state = {}
    for param in params:
        save_state[param] = Constraint.search_for_field_value(param,vehicle)

    return save_state

def run_parametric_sweep(
    vehicle:Vehicle,
    independent:str,
    dependent:str,
    ind_vals:np.ndarray
) -> None:

    out = np.empty(len(ind_vals))
    for idx,val in enumerate(ind_vals):

        new_inputs = {
            independent:val
        }
        vehicle.size_vehicle(**new_inputs)

        temp = Constraint.search_for_field_value(dependent,vehicle)
        match temp:
            case Q_(magnitude=m,units=u):
                out[idx] = temp.m
            case float():
                out[idx] = temp

    return out

def plot_sensitivity(
    independent:str,
    dependent:str,
    ind_vals:np.ndarray,
    dep_vals:np.ndarray,
    fig:figure = None,
    fig_title:str = '',
    fig_height:float=600,
    fig_width:float=600,
    line_color:str = 'blue',
    legend_label:str|None = None
) -> figure:

    if fig is None:
        fig = figure(
            frame_height=fig_height,
            frame_width=fig_width
        )

    fig.xaxis.axis_label=independent
    fig.yaxis.axis_label=dependent
    if fig_title:
        fig.title=fig_title

    fig.line(
        x=ind_vals,
        y=dep_vals,
        line_width=2,
        color=line_color,
        legend_label=legend_label 
            if legend_label is not None else dependent
    )

    return fig

def save_plots(figures:dict[str,figure],filename:str='sensitivity_plots.html') -> None:
    for fig in figures.values():
        fig.add_layout(fig.legend[0],'right')

    layout = column([fig for fig in figures.values()])
    output_file(
        filename=filename,
        title='Sensitivity Plots'
    )

    save(layout)


if __name__ == '__main__':
    
    config_path = r'C:\Users\pdwat\git\ispace_assessment\configs\vehicle_configs.yaml'
    vehicles = get_vehicles(config_path)

    sensitivies = {
        'thrust': Q_(np.linspace(5,50,10),'kN'),
        'safety_factor':np.linspace(1,5,9),
    }

    dependents = [
        'wet_mass',
        'twr',
        'mass_margin',
    ]

    figures = {}
    for _sk,_sv in sensitivies.items():
            for dependent in dependents:
                this_key = ''
                figures[f'{dependent} vs {_sk}'] = figure(
                    title=f'{dependent} vs {_sk}',
                    frame_height=600,
                    frame_width=600
                )
    
    # Setup some color options for plotting
    colors = ['blue','red','green','black']

    for vehicle,color in zip(vehicles,colors):
        save_state = save_original_states(vehicle,[key for key in sensitivies.keys()])
        for _sk,_sv in sensitivies.items():
            for dependent in dependents:
                vehicle.size_vehicle(**save_state)

                dep_vals = run_parametric_sweep(
                    vehicle=vehicle,
                    independent=_sk,
                    dependent=dependent,
                    ind_vals=_sv
                )

                match _sv:
                    case Q_(magnitude=m,units=u):
                        plot_ind = _sv.m
                    case np.ndarray():
                        plot_ind = _sv

                which_fig = f'{dependent} vs {_sk}'
                figures[which_fig] = plot_sensitivity(
                    independent=_sk,
                    dependent=dependent,
                    ind_vals=plot_ind,
                    dep_vals=dep_vals,
                    fig=figures[which_fig],
                    line_color=color,
                    legend_label=f'{vehicle.prop_system.system_type} {dependent}'
                )

    save_plots(figures)
