
# ---------------------------------------------------------
#    ____          __      ___     
#   |  _ \         \ \    / (_)    
#   | |_) | __ _ _ _\ \  / / _ ____
#   |  _ < / _` | '__\ \/ / | |_  /
#   | |_) | (_| | |   \  /  | |/ / 
#   |____/ \__,_|_|    \/   |_/___|  Simplex class
# ---------------------------------------------------------                            
# SIMaP / Jean-Luc Parouty 2022    

import numpy as np
from math import sqrt, cos, sin, acos

from barviz.SimplexBuilder import SimplexBuilder
from barviz.Scrawler       import Scrawler
from barviz.Attributes     import Attributes
from barviz.Collection     import Collection
from barviz.version        import __version__

class Simplex(Collection):

    version = __version__
    type    = 'Simplex'

    _attributes_default= { 
        'markers_colormap'     : dict( colorscale='Turbo', cmin=0, cmax=None),
        'markers_opacity'      : 1,
        'markers_size'         : 8,
        'markers_visible'      : True,
        'markers_border_color' : 'darkgray',
        'markers_border_width' : 1,
        'lines_colormap'       : dict( colorscale='Turbo', cmin=0, cmax=None),
        'lines_opacity'        : 1,
        'lines_width'          : 2,
        'lines_visible'        : True,
        'text_opacity'         : 1,
        'text_size'            : 10,
        'text_visible'         : True,
        'width'                : 500,
        'height'               : 500,
        'camera_eye'           : dict(x=.8, y=.8, z=.8),
        'camera_center'        : dict(x=0, y=0, z=0),
        'save_scale'           : 6,
        'plotly_template'      : 'plotly_white',
        'renderer'             : None
    }

    def __init__( self,  points=[], name='unknown', colors=None, labels=None, attrs={} ):
        # ---- Super init
        super(Simplex, self).__init__(points,name,colors,labels,attrs)
        # ---- Simplex version and attributes
        self.version  = Simplex.version
        self._attrs   = Attributes(attrs, Simplex._attributes_default)
        # ---- Get a Scrawler for plotting
        self.scrawler = Scrawler(self)
        # ---- Add labels/colors if undefined
        if labels is None : self.labels=[ f'P{i}' for i in range(self.nbp) ]
        if colors is None : self.colors=[ i       for i in range(self.nbp) ]
        # ---- Add colormap cmax if undefined
        if self.attrs.markers_colormap['cmax'] is None : self.attrs.markers_colormap['cmax'] = self.nbp-1
        if self.attrs.lines_colormap['cmax']   is None : self.attrs.lines_colormap['cmax']   = self.nbp-1

    @classmethod
    def build(cls, nbp=5):
        spb = SimplexBuilder()
        spb.add_points(nbp)
        spb.iterate()
        return spb.get_simplex()


    def get_skeleton(self):
        n=self.nbp
        # ---- Vertices in barycentric world
        points=np.zeros( (n,n) )
        for i in range(n):
            points[i,i]=1

        # ---- Edges
        edges,colors,labels=[],[],[]
        for i in range(0,n):
            pi = points[i]
            for j in range(i+1,n):
                pj = points[j]
                edges.extend( (pi,pj,[None]*n) )
                colors.extend( (self.colors[i], self.colors[j], 0 ) )
                labels.extend( (self.labels[i], self.labels[j], '') )

        return Collection(points=edges,name='Skeleton',colors=colors,labels=labels,attrs=self.attrs.to_dict())

    def plot(self, *args, **kwargs):
        self.scrawler.plot(*args, **kwargs)

    def plot_save(self, *save_as):
        self.scrawler.plot_save(save_as)

    def resize(self, size=2):
        self.points = self.points * size / self.diagomax
