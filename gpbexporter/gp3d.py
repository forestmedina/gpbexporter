'''
Created on 10/05/2013

@author: forestmedina
'''

import bpy;
import struct;
import math;
from bpy_extras.io_utils import ExportHelper

from bpy.utils import (
        register_class,
        unregister_class,
        )

def register():
    register_class(Exporter)
    register_class(FileHeader)
    register_class(FileBody)


def unregister():
    unregister_class(Exporter)
    unregister_class(FileHeader)
    unregister_class(FileBody)
    delete_properties()



class Reference:
    reference ="";#
    tipo =0   #
    offset =0   #
    position =0
    def __init__(self):
        self.tipo=ReferenceType.NODE;
        return;

    def writeReference(self,f):
        f.write(struct.pack("<I",len(self.reference)));#mesh
        if len(self.reference)>0:
            f.write(bytearray(self.reference,"ascii"));
        f.write(struct.pack("<I",self.tipo)),
        self.position=f.tell();
        f.write(struct.pack("<I",self.offset));
        return ;

    def writeExtra(self,f):    
        return;
        
    def writeNode(self,f):
        return;
        
    def updateOffset(self,f):
        f.seek(self.position);
        f.write(struct.pack("<I",self.offset));
        return;        

class Node(Reference):
    tipoNodo =0   #enum NodeType
    transforms =[]   #float[16]
    parent_id  =""   #string
    children   =[]  #Node[]
    camera     =None    #Camera
    light      =""   #Light
    model      =None   #Model
    
    def __init__(self):
        self.tipo=ReferenceType.NODE;
        self.tipoNodo=1;
        self.transforms=[0]*16	;
        self.camera=None;
        self.model=None;
        return;

    def writeReference(self,f):
        Reference.writeReference(self,f);
        if not self.camera is None:
            self.camera.writeReference(f);
        if not self.model is None:
            self.model.writeReference(f);
        
        
    def updateOffset(self,f):
        Reference.updateOffset(self,f);
        if not self.camera is None:
            self.camera.updateOffset(f);
        if not self.model is None:
            self.model.updateOffset(f);
       
    def writeNode(self,f):
        self.writeData(f);
        return;
    
    def writeExtra(self,f):   
        if not self.model is None:
            self.model.writeExtra(f);
        return;
    
    def writeData(self,f):
        self.offset=f.tell();
        f.write(struct.pack("<I",self.tipoNodo));
        for t in self.transforms:
            f.write(struct.pack("<f",t));
        f.write(struct.pack("<I",len(self.parent_id)+1));#mesh
        f.write(bytearray('#',"ascii"));
        if len(self.parent_id)>0:
            f.write(bytearray(self.parent_id,"ascii"));
        f.write(struct.pack("<I",0)),#hijos longitud de cadena 0
        if not self.camera is None:
            self.camera.writeData(f);
        else:
            f.write(struct.pack("B",0));
        f.write(struct.pack("B",0));#luz longitud de cadena 0
        if not self.model is None:
            self.model.writeData(f);
        else:
            f.write(struct.pack("<I",1));#mesh
            f.write(bytearray('#',"ascii"));
        return ;


class Model (Reference):
    mesh     =""   #Mesh
    meshSkin =""    #MeshSkin
    materials=[]     #Material[]
    def __init__(self):
        self.tipo=ReferenceType.MODEL;
        return;

    def writeReference(self,f):
        self.mesh.writeReference(f);
        return;
        
    def updateOffset(self,f):
        self.mesh.updateOffset(f);
        return;
        
    def writeNode(self,f):
        return;
    
    def writeExtra(self,f):  
        self.mesh.writeData(f);
        return;
    
    def writeData(self,f):
        f.write(struct.pack("<I",len(self.mesh.reference)+1));#mesh
        f.write(bytearray('#',"ascii"));
        if len(self.mesh.reference)>0:
            f.write(bytearray(self.mesh.reference,"ascii"));
        f.write(struct.pack("B",0));#meshSkin longitud de cadena 0
        f.write(struct.pack("<I",0));#material longitud de arreglo 0
        return ;

class Mesh(Reference):
    vertexFormat ="";
    vertices    =[];
    boundingBox ="";
    boundingSphere="";
    parts="";
    def __init__(self):
        self.tipo=ReferenceType.MESH;
        return;

    def writeData(self,f):
        self.offset=f.tell();
        f.write(struct.pack("<I",2));#Cantidad de vertexUsage
        f.write(struct.pack("<I",1));#VextexUsage 1-POSITION
        f.write(struct.pack("<I",3));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<I",2));#VextexUsage 2-NORMAL
        f.write(struct.pack("<I",3));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<I",len(self.vertices)*24));#Cantidad de Vertices * 3(Position vertice) * 3 (Normal Vertice) Omitting any other vertice information
        for v in self.vertices:
            f.write(struct.pack("<f",v.co[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.co[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.co[2]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.normal[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.normal[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.normal[2]));#VextexSize 3 (x,y,z)
        #Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box


        #Omit bounding sphere
        f.write(struct.pack("<f",0));#Omit bounding sphere
        f.write(struct.pack("<f",0));#Omit bounding sphere
        f.write(struct.pack("<f",0));#Omit bounding sphere
        f.write(struct.pack("<f",0));#Omit bounding sphere
        f.write(struct.pack("<I",1));#MeshPart Array of only 1 part
        f.write(struct.pack("<I",4));#GL_TRIANGLES
        f.write(struct.pack("<I",5125));#Unsigned int Index format
        f.write(struct.pack("<I",len(self.parts)*3*4));#Unsigned int Index format
        for p in self.parts:
            f.write(struct.pack("<I",p.vertices[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<I",p.vertices[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<I",p.vertices[2]));#VextexSize 3 (x,y,z)
        return ;
        
        

class Camera(Reference):
    cameraType =0#byte {perspective|orthographic}
    aspectRatio =0.0#float
    nearPlane =0.0#float
    farPlane =0.0#float
    fieldOfView =0.0 #[ cameraType : perspective
                #  fieldOfView float
                #]
                #[ cameraType : orthographic
                #  magnification float[2]
                #]
    def __init__(self):
        self.tipo=ReferenceType.CAMERA;
        return;

    def writeData(self,f):
        self.offset=f.tell();
        f.write(struct.pack("B",self.cameraType));#VextexUsage 2-POSITION
        f.write(struct.pack("<f",self.aspectRatio));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<f",self.nearPlane));#VextexUsage 2-NORMAL
        f.write(struct.pack("<f",self.farPlane));#VextexUsage 2-NORMAL
        f.write(struct.pack("<f",self.fieldOfView));#VextexSize 3 (x,y,z)
        return ;        


class ReferenceType:
    SCENE=1;
    NODE=2;
    MODEL=11;
    MESH=34;
    CAMERA=34;


class NodeType:
    NODE = 1,
    JOINT = 2



class Exporter(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_gameplay.gpb";
    bl_label        = "Gameplay3d Exporter";
    bl_options      = {'PRESET'};
    filename_ext    = ".gpb";
    objetos=[];
    

    def procesarMesh(self, bobject):
        mesh = bobject.to_mesh(bpy.context.scene,True,'PREVIEW');
        meshes_to_clear.append(mesh);
        node= Node();
        node.transforms[0]=bobject.matrix_world[0][0];
        node.transforms[1]=bobject.matrix_world[1][0];
        node.transforms[2]=bobject.matrix_world[2][0];
        node.transforms[3]=bobject.matrix_world[3][0];
        node.transforms[4]=bobject.matrix_world[0][1];
        node.transforms[5]=bobject.matrix_world[1][1];
        node.transforms[6]=bobject.matrix_world[2][1];
        node.transforms[7]=bobject.matrix_world[3][1];
        node.transforms[8]=bobject.matrix_world[0][2];
        node.transforms[9]=bobject.matrix_world[1][2];
        node.transforms[10]=bobject.matrix_world[2][2];
        node.transforms[11]=bobject.matrix_world[3][2];
        node.transforms[12]=bobject.matrix_world[0][3];
        node.transforms[13]=bobject.matrix_world[1][3];
        node.transforms[14]=bobject.matrix_world[2][3];
        node.transforms[15]=bobject.matrix_world[3][3];
        #node.transforms[0]=0;
        #node.transforms[1]=0;
        #node.transforms[2]=0;
        #node.transforms[3]=0;
        #node.transforms[4]=0;
        #node.transforms[5]=0;
        #node.transforms[6]=0;
        #node.transforms[7]=0;
        #node.transforms[8]=0;
        #node.transforms[9]=0;
        #node.transforms[10]=0;
        #node.transforms[11]=0;
        #node.transforms[12]=bobject.location[0];
        #node.transforms[13]=bobject.location[1];
        #node.transforms[14]=bobject.location[2];
        #node.transforms[15]=0;
        node.model=Model();
        node.model.mesh=Mesh();
        node.reference=bobject.name;
        node.model.mesh.reference=bobject.name+"mesh";
        node.model.mesh.vertices=mesh.vertices;
        node.model.mesh.parts=mesh.polygons;
        return node;
        
        
    def procesarCamera(self, cam):
        bobject=bpy.data.objects[cam.name];
        node= Node();
        node.transforms[0]=bobject.matrix_world[0][0];
        node.transforms[1]=bobject.matrix_world[1][0];
        node.transforms[2]=bobject.matrix_world[2][0];
        node.transforms[3]=bobject.matrix_world[3][0];
        node.transforms[4]=bobject.matrix_world[0][1];
        node.transforms[5]=bobject.matrix_world[1][1];
        node.transforms[6]=bobject.matrix_world[2][1];
        node.transforms[7]=bobject.matrix_world[3][1];
        node.transforms[8]=bobject.matrix_world[0][2];
        node.transforms[9]=bobject.matrix_world[1][2];
        node.transforms[10]=bobject.matrix_world[2][2];
        node.transforms[11]=bobject.matrix_world[3][2];
        node.transforms[12]=bobject.matrix_world[0][3];
        node.transforms[13]=bobject.matrix_world[1][3];
        node.transforms[14]=bobject.matrix_world[2][3];
        node.transforms[15]=bobject.matrix_world[3][3];
        node.camera=Camera();
        node.reference=cam.name;
        node.camera.reference=cam.name+"cam";
        node.camera.cameraType=1;
        node.camera.aspectRatio=1.700000;
        node.camera.nearPlane=cam.clip_start;
        node.camera.farPlane=cam.clip_end;
        node.camera.fieldOfView=math.degrees(cam.angle);
        return node;        
        
    def execute(self, context):
        global meshes_to_clear;
        meshes_to_clear=[];
        bpy.ops.object.mode_set(mode='OBJECT');
        # Set the default return state to FINISHED
        result = {'FINISHED'};
        # Check that the currently selected object contains mesh data for exporting
        self.objetos=[];
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                node = self.procesarMesh(ob);
                self.objetos.append(node);
        # Create a file header object with data stored in the body section   
        # Open the file for writing
        camera = self.procesarCamera(bpy.data.cameras[bpy.context.scene.camera.name]);
        self.objetos.append(camera);
        file = open(self.filepath, 'bw');
        file.write(b'\xABGPB\xBB\r\n\x1A\n');
        file.write(struct.pack("B",1));
        file.write(struct.pack("B",2));
        file.write(struct.pack("<I",len(self.objetos)*2+1));#+1 for scene reference , *2 for node+mesh reference and node+camera reference 
        scene=Reference();
        scene.tipo=ReferenceType.SCENE;
        scene.reference="__SCENE__";
        scene.writeReference(file);
        for o in  self.objetos:
            o.writeReference(file);
        scene.offset=file.tell();
        file.write(struct.pack("<I",len(self.objetos)));
        for o in  self.objetos:
            o.writeNode(file);
        for o in  self.objetos:
            o.writeExtra(file);
#write data of scene
        file.write(struct.pack("<I",len(camera.reference)+1));#camara xref
        file.write(bytearray('#',"ascii"));
        if len(camera.reference)>0:
            file.write(bytearray(camera.reference,"ascii"));
        file.write(struct.pack("<f",1.0));
        file.write(struct.pack("<f",1.0));
        file.write(struct.pack("<f",1.0));
        for o in  self.objetos:
            o.updateOffset(file);
        scene.updateOffset(file);
        file.close();
        for m in meshes_to_clear:
            bpy.data.meshes.remove(m);
        return result;



