import os
import xml.etree.ElementTree as ET
from ..tools import xmlhelper

class Texture:

    def __init__(self):
        self.name = "" #pull name from filename?
        self.unk32 = 0
        self.usage = "" #enum?
        self.usage_flags = [] #enum?
        self.extra_flags = 0
        self.width = 0
        self.height = 0
        self.miplevels = 0
        self.format = "" #enum?
        self.filename = ""

    def read_xml(self, root):
        self.name = root.find("Name").text
        self.unk32 = xmlhelper.ReadInt(root.find("Unk32"))
        self.usage = root.find("Usage").text #ENUM?
        usage_flags = root.find("UsageFlags")
        if usage_flags is not None:
            self.usage_flags = usage_flags.text.split(", ")

        self.extra_flags = xmlhelper.ReadInt(root.find("ExtraFlags"))
        self.width = xmlhelper.ReadInt(root.find("Width"))
        self.height = xmlhelper.ReadInt(root.find("Height"))
        self.miplevels = xmlhelper.ReadInt(root.find("MipLevels"))
        self.format = root.find("Format").text
        self.filename = root.find("FileName").text

class TextureDictionary:

    def __init__(self):
        self.textures = [] #of textures 

    def read_xml(self, root):
        for node in root:
            t = Texture()
            t.read_xml(node)
            self.textures.append(t)

    def to_dict(self):
        dict = {}
        for tex in self.textures:
            dict[tex.name] = tex
        
        return dict

class ShaderParameter:

    def __init__(self):
        self.name = ""
        self.type = ""

    def read_xml(self, root):
        self.name = root.attrib["name"]
        self.type = root.attrib["type"]

class ShaderTextureParameter(ShaderParameter):

    def __init__(self):
        super().__init__()
        self.texture_name = "givemechecker"

    def read_xml(self, root):
        super().read_xml(root)
        name = root.find("Name")
        if (name is not None):
            self.texture_name = name.text

class ShaderValueParameter(ShaderParameter):

    def __init__(self):
        super().__init__()
        self.value = []

    def read_xml(self, root):
        super().read_xml(root)
        self.value = xmlhelper.ReadQuaternion(root)

class Shader:

    def __init__(self):
        self.name = ""
        self.filename = None
        self.parameters = []

    def read_xml(self, root):
        name = root.find("Name")
        if (name is not None):
            self.name = name.text
        
        filename = root.find("FileName")
        if (filename is not None):
            self.filename = filename.text

        for node in root.find("Parameters"):
            if(node.attrib["type"] == "Texture"):
                p = ShaderTextureParameter()
                p.read_xml(node)
                self.parameters.append(p)
            else:
                p = ShaderValueParameter()
                p.read_xml(node)
                self.parameters.append(p)

class ShaderGroup:

    def __init__(self):
        self.unknown_30 = 0
        self.texture_dictionary = None
        self.shaders = [] 
    
    def read_xml(self, root):
        self.unknown_30 = xmlhelper.ReadFloat(root.find("Unknown30"))

        node = root.find("TextureDictionary")

        if(node != None):
            texture_dictionary = TextureDictionary()
            texture_dictionary.read_xml(node)

            self.texture_dictionary = texture_dictionary

        for node in root.find("Shaders"):
            s = Shader()
            s.read_xml(node)
            self.shaders.append(s)

class ShaderManager:

    def __init__(self):
        self.shaderxml = os.path.join(os.path.dirname(__file__), 'Shaders.xml')
        self.shaders = {}
        self.load_shaders()

    def load_shaders(self):
        tree = ET.parse(self.shaderxml)
        for node in tree.getroot():
            s = Shader()
            s.read_xml(node)
            self.shaders[s.name] = s