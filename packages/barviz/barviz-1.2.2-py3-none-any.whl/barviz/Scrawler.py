
# ---------------------------------------------------------
#    ____          __      ___     
#   |  _ \         \ \    / (_)    
#   | |_) | __ _ _ _\ \  / / _ ____
#   |  _ < / _` | '__\ \/ / | |_  /
#   | |_) | (_| | |   \  /  | |/ / 
#   |____/ \__,_|_|    \/   |_/___|  Scrawler class
# ---------------------------------------------------------                            
# SIMaP / Jean-Luc Parouty 2022    

from barviz.Collection import Collection
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from barviz.version        import __version__

import random
from collections.abc import Iterable


class Scrawler:

    version = __version__

    def __init__(self, simplex=None):
        self.simplex    = simplex
        self.fig        = None

    def barycentric_to_3d(self,collection):
        vertices = self.simplex.points
        points   = collection.points
        nbp      = collection.nbp

        p3d = np.zeros( (nbp,3) )

        for i,p in enumerate(points):
            if None in p:
                p3d[i] = np.array([None,None,None])
            else:
                p3d[i] = p.dot(vertices)

        return p3d


    def update_center(self, observed_point):
        '''
        Get an observable point and update the plotly camera center position
        args :
            observable_point : point or collection
        return:
            None
        '''
        axe_max    = self.simplex.diagomax
        attrs      = self.simplex.attrs

        # We want a collection
        if not isinstance(observed_point, Collection):
            observed_point = Collection([observed_point])
         
        # Projection in barycentric coord.
        p3d = self.barycentric_to_3d(observed_point)
        # Supression of possible (None,None,None) 
        p3d = np.array( [ p for p in p3d if not None in p  ] )
        # Mean of cloud points
        (xp,yp,zp) = p3d.mean(axis=0)
        # Update camera_center
        attrs.camera_center = dict( x=(xp)/(2*axe_max), y=(yp)/(2*axe_max), z=(zp)/(2*axe_max) )


    def _get_layout(self):
        attrs     = self.simplex.attrs
        axe_max   = self.simplex.diagomax
        layout = dict( 
            width       = attrs.width, 
            height      = attrs.height,
            template    = attrs.plotly_template,
            autosize    = False,
            showlegend  = False,
            margin      = dict(l=0, r=0, t=0, b=0, pad=0),
            scene_xaxis = dict(nticks=10, range=[-axe_max, axe_max], visible=False),
            scene_yaxis = dict(nticks=10, range=[-axe_max, axe_max], visible=False),
            scene_zaxis = dict(nticks=10, range=[-axe_max, axe_max], visible=False),
            # scene_aspectratio   = dict( x=1, y=1, z=1 ),
            scene_aspectmode    = 'cube',
            scene_camera_eye    = attrs.camera_eye,
            scene_camera_center = attrs.camera_center
        )
        return layout

    def _get_config(self):
        attrs   = self.simplex.attrs
        config = {
            'toImageButtonOptions': {
                'format': 'png', 
                'filename': self.simplex.name,
                'width':  attrs.width,
                'height': attrs.height,
                'scale':  attrs.save_scale
            }
        }
        return config



    def _get_collection_labels(self,collection):
        lc = collection.labels
        ls = self.simplex.labels
        # ---- Labels still defined
        if lc is not None : return lc
        # ---- No labels
        labels=[]
        for p in collection.points:
            label=''
            for i,v in enumerate(p):
                label += f'{ls[i]} : {v}<br>'
            labels.append(label)
        return labels


    def _trace_collection(self, collection):
        attrs  = collection.attrs
        colors = collection.colors
        labels = self._get_collection_labels(collection)
        p      = self.barycentric_to_3d(collection)

        # ---- Markers
        #
        trace1 = go.Scatter3d(x=p[:, 0], y=p[:, 1], z=p[:, 2],
                              mode      = 'markers',
                              visible   = attrs.markers_visible,
                              hovertext = labels, 
                              hoverinfo = "text",
                              marker    = dict(color      = colors,
                                               opacity    = attrs.markers_opacity,
                                               colorscale = attrs.markers_colormap['colorscale'], 
                                               cmin       = attrs.markers_colormap['cmin'], 
                                               cmax       = attrs.markers_colormap['cmax'],
                                               size       = attrs.markers_size,
                                               line       = dict(width=attrs.markers_border_width, color = attrs.markers_border_color)))
        # ---- Lines
        #
        trace2 = go.Scatter3d(x=p[:, 0], y=p[:, 1], z=p[:, 2],
                              mode      = 'lines',
                              visible   = attrs.lines_visible,
                              opacity   = attrs.lines_opacity,
                              hovertext = [],
                              hoverinfo = 'skip',
                              line      = dict(color      = colors,
                                               colorscale = attrs.lines_colormap['colorscale'], 
                                               cmin       = attrs.lines_colormap['cmin'], 
                                               cmax       = attrs.lines_colormap['cmax'],
                                               width      = attrs.lines_width))
        # ---- Text
        #
        trace3 = go.Scatter3d(x=p[:, 0], y=p[:, 1], z=p[:, 2],
                              mode      = 'text',
                              visible   = attrs.text_visible,
                              opacity   = attrs.text_opacity,
                              hovertext = [],
                              hoverinfo = 'skip',
                              text      = labels,
                              textfont  = dict(size       = attrs.text_size))

        return [trace1, trace2, trace3]



    def plot(self, *stuffs, save_as=None, observed_point=None):

        attrs     = self.simplex.attrs

        # ---- Simplex Skeleton
        renderer = attrs.renderer
        skeleton = self.simplex.get_skeleton()
        traces   = self._trace_collection(skeleton)

        # ---- Add stuffs : collections as traces
        if stuffs is not None:
            for c in stuffs:
                traces.extend( self._trace_collection(c) )
                
        fig = go.Figure(data=[ *traces ])

        # ---- Observed point 
        if observed_point is not None:
            self.update_center(observed_point)

        # ---- Set layout
        fig.update_layout( self._get_layout() )

        # ---- Show it
        fig.show( config=self._get_config(), renderer=renderer )
        self.fig = fig

        # ---- Save option
        self.plot_save(save_as)


    def plot_save(self, save_as):
        attrs=self.simplex.attrs

        # ---- No save
        #
        if save_as is None : return

        # ---- Convert to a tuple if needed
        #
        if isinstance(save_as, str) : 
            save_as = (save_as,) 

        if not isinstance(save_as, Iterable) : 
            raise AttributeError('"save_as" must be str or list')

        # ---- Save it
        #
        for filename in save_as:
            if filename.endswith('.html') : 
                # ---- Save as html
                #
                fig=go.Figure(self.fig)
                fig.update_layout( dict(width=None, height=None, autosize=True) )
                pio.write_html(fig, filename)
            else:
                # ---- Save as an image
                #
                scale = attrs.save_scale
                size  = min(attrs.width, attrs.height)
                pio.write_image(self.fig, filename, width=size, height=size, scale=scale)
                
            print('Saved as : ', filename)



