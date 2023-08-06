
# ---------------------------------------------------------
#    ____          __      ___     
#   |  _ \         \ \    / (_)    
#   | |_) | __ _ _ _\ \  / / _ ____
#   |  _ < / _` | '__\ \/ / | |_  /
#   | |_) | (_| | |   \  /  | |/ / 
#   |____/ \__,_|_|    \/   |_/___|  Collection class
# ---------------------------------------------------------                            
# SIMaP / Jean-Luc Parouty 2022   

import numpy as np
import json
import pathlib
from barviz.Attributes     import Attributes
from barviz.version        import __version__


class Collection:

    version = __version__
    type    = 'Collection'

    _attributes_default= { 
        'markers_colormap'     : dict( colorscale=['gray','gray'], cmin=0, cmax=None),
        'markers_opacity'      : 0.6,
        'markers_size'         : 6,
        'markers_visible'      : True,
        'markers_border_color' : None,
        'markers_border_width' : 1,
        'lines_colormap'       : dict( colorscale=['gray','gray'], cmin=0, cmax=None),
        'lines_opacity'        : 1,
        'lines_width'          : 2,
        'lines_visible'        : False,
        'text_opacity'         : 1,
        'text_size'            : 10,
        'text_visible'         : False,
    }


    def __init__(self,  points=[], name='unknown', colors=None, labels=None, attrs={} ):
        self.version  = Collection.version
        self._attrs   = Attributes(attrs, Collection._attributes_default)
        self.name     = name
        self.points   = np.array(points)
        self.colors   = colors
        self.labels   = labels 
        # ---- Add labels/colors if undefined
        if labels is None : self.labels=[ f'C{i}' for i in range(self.nbp) ]
        if colors is None : self.colors=[ i       for i in range(self.nbp) ]
        # ---- Add colormap cmax if undefined
        if self.attrs.markers_colormap['cmax'] is None : self.attrs.markers_colormap['cmax'] = self.nbp-1
        if self.attrs.lines_colormap['cmax']   is None : self.attrs.lines_colormap['cmax']   = self.nbp-1


    def save_as(self, filename):
        # ---- Prepare data
        data = dict( 
            version   = self.version, 
            attrs     = self.attrs.to_dict(),
            name      = self.name,
            points    = self.points.tolist(),
            colors    = self.colors,
            labels    = self.labels
        )
        # ---- Create parents directories if needed
        pathlib.Path(filename).parent.mkdir(parents=True, exist_ok=True) 
        # ---- Save data as json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print(f'Saved ({filename}).')


    @classmethod
    def load(cls, filename):
        # ---- Load json
        with open(filename) as jf:
            data = json.load(jf)
        # ---- Get a simplex
        sp = cls(points=data['points'], name=data['name'], colors=data['colors'], labels=data['labels'], attrs=data['attrs'])
        print(f'Loaded ({filename}).')
        return sp


    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self,attributes):
        self._attrs = Attributes(attributes, self._attributes_default)


    @property
    def nbp(self):
        return len(self.points)

    @property
    def diagomax(self):
        dm = -1
        for pi in self.points:
            if None not in pi : dm = max( dm, np.sqrt(pi.dot(pi)) )
        return dm


    def __repr__(self):
        return f'<Collection "{self.name}" with {self.nbp} points>'


    def __str__(self):
        p,c = self.points, self.colors
        out  = f'==== {self.type} : {self.name} ====\n'
        out += f'Version  : {self.version}\n'
        out += f'diagomax : {self.diagomax:.2f}\n' 
        out += f'Points   : {self.nbp}\n'
        for i,pi in enumerate(p[:25]):
            out += f'    {pi}   c={c[i]}\n'
        if self.nbp>25: out+='    (...)\n'
        return out

