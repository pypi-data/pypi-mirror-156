import math
from ..unit.types import UnitsConvertor, Units

# the value indicating that angular value is expressed in some unit
AngularRadian = 0
AngularDegree = 1
AngularMOA = 2
AngularMil = 3
AngularMRad = 4
AngularThousand = 5
AngularInchesPer100Yd = 6
AngularCmPer100M = 7


class AngularConvertor(UnitsConvertor):
    unit_type = 'angular'

    _units = {
        AngularRadian: {'name': 'rad', 'accuracy': 6,
                        'to': lambda v: v,
                        'from': lambda v: v},
        AngularDegree: {'name': '°', 'accuracy': 4,
                        'to': lambda v: v / 180 * math.pi,
                        'from': lambda v: v * 180 / math.pi},
        AngularMOA: {'name': 'moa', 'accuracy': 2,
                     'to': lambda v: v / 180 * math.pi / 60,
                     'from': lambda v: v * 180 / math.pi * 60},
        AngularMil: {'name': 'mil', 'accuracy': 2,
                     'to': lambda v: v / 3200 * math.pi,
                     'from': lambda v: v * 3200 / math.pi},
        AngularMRad: {'name': 'mrad', 'accuracy': 2,
                      'to': lambda v: v / 1000,
                      'from': lambda v: v * 1000},
        AngularThousand: {'name': 'ths', 'accuracy': 2,
                          'to': lambda v: v / 3000 * math.pi,
                          'from': lambda v: v * 3000 / math.pi},
        AngularInchesPer100Yd: {'name': 'in/100yd', 'accuracy': 2,
                                'to': lambda v: math.atan(v / 3600),
                                'from': lambda v: math.tan(v) * 3600},
        AngularCmPer100M: {'name': 'cm/100m', 'accuracy': 2,
                           'to': lambda v: math.atan(v / 10000),
                           'from': lambda v: math.tan(v) * 10000},
    }


class Angular(Units):
    """ Angular object keeps information about angular units """
    convertor = AngularConvertor

    def __init__(self, value: float, units: int):
        super(Angular, self).__init__(value, units)
