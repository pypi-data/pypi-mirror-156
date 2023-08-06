
# ---------------------------------------------------------
#    ____          __      ___     
#   |  _ \         \ \    / (_)    
#   | |_) | __ _ _ _\ \  / / _ ____
#   |  _ < / _` | '__\ \/ / | |_  /
#   | |_) | (_| | |   \  /  | |/ / 
#   |____/ \__,_|_|    \/   |_/___|  Attributes class
# ---------------------------------------------------------                            
# SIMaP / Jean-Luc Parouty 2022    

import json

class Attributes(object):

    def __init__(self, attributes, defaults={}):
        attrs=self.__dict__
        if isinstance(attributes, Attributes) :
            attributes=attributes.to_dict()
        for k,v in defaults.items():
            if isinstance(v,dict): v=dict(v)   # Need a copy !
            attrs[k]=attributes.get(k,v)

    def __getattr__(self, name):
        '''Get an attribute, if exist'''
        attrs=self.__dict__
        if name in attrs:
            return attrs[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        '''Set an attribute value, if it already exist'''
        attrs=self.__dict__
        if name in attrs:
            attrs[name]=value
        else:
            raise AttributeError("No such attribute: " + name)

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)

    def __repr__(self):
        attrs=self.__dict__
        out = 'Available attributes are :\n'
        for k,v in attrs.items():
            if not k.startswith('_') : out += f'    {k:18s} = {v}\n'
        return out