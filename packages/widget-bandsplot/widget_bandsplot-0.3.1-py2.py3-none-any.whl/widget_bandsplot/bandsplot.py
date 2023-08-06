from turtle import Turtle
import ipywidgets as widgets
from traitlets import Unicode, List, Dict, Float, Bool
from copy import deepcopy
import numpy as np

# See js/lib/example.js for the frontend counterpart to this file.

@widgets.register
class BandsPlotWidget(widgets.DOMWidget):
    """A Jupyter widget to plot bandstructures and DOS."""

    # Name of the widget view class in front-end
    _view_name = Unicode('BandsplotView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('BandsplotModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode('widget-bandsplot').tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode('widget-bandsplot').tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.2.4').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.2.4').tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.
    value = Unicode('This is bandsplot!').tag(sync=True)

    #Json fils for the bandstructures
    bands = List().tag(sync=True) 

    #Json file for the DOS plot
    dos = Dict().tag(sync=True)

    #The total DOS data x, y
    tdos_x = List().tag(sync=True)
    tdos_y = List().tag(sync=True)

    #yLimit for the plot
    energy_range = Dict({"ymin": -10.0, "ymax": 10.0}).tag(sync=True)

    #Band and DOS Fermi energy
    band_fermienergy = List().tag(sync=True)
    dos_fermienergy = Float().tag(sync=True)

    #Visiblity for the Fermi energy level
    plot_fermilevel = Bool(True).tag(sync=True)

    #The Legend for the density of states
    show_legend = Bool(True).tag(sync=True)

    #Whether is spin polarized calculations
    spin_polarized = Bool(False).tag(sync=True)

    def __init__(self, bands=None, dos=None, fermi_energy = None, show_legend = True,
                 plot_fermilevel = True, energy_range = {"ymin": -10.0, "ymax": 10.0}):
    
        if bands == None and dos == None:
            raise ImportError("You need give band structure or DOS files.")

        super().__init__(show_legend = show_legend, plot_fermilevel = plot_fermilevel, energy_range = energy_range)

        if bands is not None:
            self.bands = bands
            
            for i in bands:
                self.band_fermienergy.append(i['fermi_level'])
        
        if dos is not None:
            temp_dos = deepcopy(dos)

            if 'dos_spin_up | states/eV' in temp_dos['tdos']['values'] and 'dos_spin_down | states/eV' in temp_dos['tdos']['values']:
                self.spin_polarized = True

            self.tdos_x = dos['tdos']['energy | eV']['data']
            self.tdos_y = dos['tdos']['values']['dos | states/eV']['data']
            self.dos_fermienergy = dos['fermi_energy']

            tx = np.array(self.tdos_x)
            ty = np.array(self.tdos_y)

            index = np.where(np.logical_and(tx > energy_range['ymin']+self.dos_fermienergy, tx < energy_range['ymax']+self.dos_fermienergy))

            temp_dos['tdos']['energy | eV']['data'] = tx[index].tolist()
            temp_dos['tdos']['values']['dos | states/eV']['data'] = ty[index].tolist()

            if self.spin_polarized:
                tot_up = np.array(dos['tdos']['values']['dos_spin_up | states/eV']['data'])[index].tolist()
                tot_dn = np.array(dos['tdos']['values']['dos_spin_down | states/eV']['data'])[index].tolist()
                temp_dos['tdos']['values']['dos_spin_up | states/eV']['data'] = tot_up
                temp_dos['tdos']['values']['dos_spin_down | states/eV']['data'] = tot_dn

            pdos_names = []
            temp_dos['pdos'] = []
            for i in deepcopy(dos['pdos']):
                if '-' in i['orbital']:
                    name = i['kind'] + i['orbital'][0] + ' ' + i['orbital'].split('-')[-1]
                    i['orbital'] = i['orbital'][0] + ' ' + i['orbital'].split('-')[-1]
                else:
                    name = i['kind'] + i['orbital'][0]
                    i['orbital'] = i['orbital'][0] 
                if name not in pdos_names:
                    pdos_names.append(name)
                    temp_dos['pdos'].append(i)
                else:
                    a = temp_dos['pdos'][pdos_names.index(name)]['pdos | states/eV']['data']
                    b = i['pdos | states/eV']['data']
                    temp_dos['pdos'][pdos_names.index(name)]['pdos | states/eV']['data'] = np.add(a, b).tolist()

            for i,j in enumerate(temp_dos['pdos']):
                tx = j['energy | eV']['data']
                ty = j['pdos | states/eV']['data']

                tx = np.array(tx)
                ty = np.array(ty)

                index = np.where(np.logical_and(tx > energy_range['ymin']+self.dos_fermienergy, tx < energy_range['ymax']+self.dos_fermienergy))

                if 'dn' in j['orbital']:
                    temp_dos['pdos'][i]['pdos | states/eV']['data'] = (-ty[index]).tolist()
                else:
                    temp_dos['pdos'][i]['pdos | states/eV']['data'] = ty[index].tolist()

                temp_dos['pdos'][i]['energy | eV']['data'] = tx[index].tolist()

            self.dos = deepcopy(temp_dos)
            
                 




