# Copyright (c) Thales.


from numbers import Number
from ipywidgets import DOMWidget, register
from traitlets import Int, List, Unicode
from ._frontend import module_name, module_version


@register
class SatelliteMonitorWidget(DOMWidget):
    _model_name = Unicode('SatelliteMonitorModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('SatelliteMonitorView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    satellites = List([]).tag(sync=True)
    width = Int(800).tag(sync=True)
    height = Int(600).tag(sync=True)

    def __init__(self, **kwargs):
        if (kwargs['satellites']):
            print(kwargs['satellites'])
            for index, value in enumerate(kwargs['satellites']):
                if isinstance(value, SatelliteDTO):
                    kwargs['satellites'][index] = kwargs['satellites'][index].__dict__

        super().__init__(**kwargs)


class SatelliteDTO():
    name: str
    x: Number
    y: Number
    z: Number

    def __init__(self, name: str, x: Number, y: Number, z: Number):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
