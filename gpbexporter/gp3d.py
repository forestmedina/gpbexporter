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
        global reference_count;
        reference_count+=1;
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
    childrens   =[]  #Node[]
    camera     =None    #Camera
    light      =""   #Light
    model      =None   #Model
    
    def __init__(self):
        self.tipo=ReferenceType.NODE;
        self.tipoNodo=1;
        self.transforms=[0]*16;
        self.camera=None;
        self.light=None;
        self.model=None;
        self.childrens=[];
        self.parent_id=None;
        return;

    def writeReference(self,f):
        Reference.writeReference(self,f);
        for c in self.childrens:
            c.writeReference(f);
        if not self.camera is None:
            self.camera.writeReference(f);
        if not self.model is None:
            self.model.writeReference(f);
        
        
    def updateOffset(self,f):
        Reference.updateOffset(self,f);
        for c in self.childrens:
            c.updateOffset(f);
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
        for c in self.childrens:
            c.writeExtra(f);
        return;
    
    def writeData(self,f):
        self.offset=f.tell();
        f.write(struct.pack("<I",self.tipoNodo));
        for t in self.transforms:
            f.write(struct.pack("<f",t));
        if not self.parent_id is None:
            f.write(struct.pack("<I",len(self.parent_id)));#mesh
            if len(self.parent_id)>0:
                f.write(bytearray(self.parent_id,"ascii"));
        else:
            f.write(struct.pack("<I",0));
        f.write(struct.pack("<I",len(self.childrens))),#hijos longitud de cadena 0
        if len(self.childrens)>0:
            for c in self.childrens:
                c.writeData(f);
        if not self.camera is None:
            self.camera.writeData(f);
        else:
            f.write(struct.pack("B",0));
            
        if not self.light is None:
            self.light.writeData(f);
        else:
            f.write(struct.pack("B",0));#luz longitud de cadena 0
        if not self.model is None:
            self.model.writeData(f);
        else:
            f.write(struct.pack("<I",0));#mesh
        return ;


class Model (Reference):
    mesh     =""   #Mesh
    meshSkin =""    #MeshSkin
    materials=[]     #Material[]
    def __init__(self):
        self.tipo=ReferenceType.MODEL;
        self.meshSkin=None;
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
        if self.meshSkin is None:
            f.write(struct.pack("B",0));#hasMeshSkin no
        else:
            f.write(struct.pack("B",1));#hasMeshSkin yes
            self.meshSkin.writeData(f);
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
        f.write(struct.pack("<I",4));#Cantidad de vertexUsage
        f.write(struct.pack("<I",1));#VextexUsage 1-POSITION
        f.write(struct.pack("<I",3));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<I",2));#VextexUsage 2-NORMAL
        f.write(struct.pack("<I",3));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<I",7));#VextexUsage 7-BLENDINDICES
        f.write(struct.pack("<I",4));#VextexSize 4 max joints
        f.write(struct.pack("<I",6));#VextexUsage 6-BLENDWEIGTHS
        f.write(struct.pack("<I",4));#VextexSize 4 max joints
        f.write(struct.pack("<I",len(self.vertices)*(3+3+4+4)*4));#Cantidad de Vertices * 3(Position vertice) * 3 (Normal Vertice) Omitting any other vertice information

        for v in self.vertices:
            f.write(struct.pack("<f",v.co[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.co[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.co[2]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.normal[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.normal[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.normal[2]));#VextexSize 3 (x,y,z)
            ngroups=0;
            #print("<g");
            for g in v.groups:
                f.write(struct.pack("<f",g.group));
                #print(g.group);
                ngroups+=1;
                if ngroups>=4:
                    break;
            #print("-");
            while ngroups<4:
                f.write(struct.pack("<f",0));#VextexSize 3 (x,y,z)
                #print(0);
                ngroups+=1;
            #print("g>");    
            ngroups=0;
            #print("<w");
            for g in v.groups:
                f.write(struct.pack("<f",g.weight));
                ngroups+=1;
                #print(g.weight);
                if ngroups>=4:
                    break;
           # print("-");   
            while ngroups<4:
                f.write(struct.pack("<f",0));#VextexSize 3 (x,y,z)
                #print(0);
                ngroups+=1;
            #print("w>");
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
        
class MeshSkin(Reference):
    
    def __init__(self):
        self.tipo=ReferenceType.MESHSKIN;
        self.bindShape=[0]*16   ;
        self.joints=[];
        self.jointBindPoses=[];
        self.boundingBox=None;
        self.boundingSphere=None;
        return;

    def writeData(self,f):
        self.offset=f.tell();
        print("BindShape "+str(len(self.bindShape)));
        for b in self.bindShape:
            f.write(struct.pack("<f",b));
        f.write(struct.pack("<I",len(self.joints)));#joints
        for j in self.joints:
            f.write(struct.pack("<I",len(j.reference)+1));#mesh
            f.write(bytearray('#',"ascii"));
            f.write(bytearray(j.reference,"ascii"));

        f.write(struct.pack("<I",len(self.joints)*16));#joints
        for b in self.jointBindPoses:
            f.write(struct.pack("<f",b));
        #Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #Omit bounding sphere
        #f.write(struct.pack("<f",0));#Omit bounding sphere
        #f.write(struct.pack("<f",0));#Omit bounding sphere
        #f.write(struct.pack("<f",0));#Omit bounding sphere
        #f.write(struct.pack("<f",0));#Omit bounding sphere
        return ;   
        
        
#cesar
class Light(Reference):
    lightType = None#byte, see LampType class
    color = []#float r b g 
    range = 0.0#float
    innerAngle=0.0#float
    outerAngle=0.0#float
    def __init__(self):
        self.tipo=ReferenceType.LIGHT;
        self.color = [1.0, 1.0, 1.0];
        return;
    
    def writeData(self, f):
        self.offset=f.tell();
        print("lamp writeData %d"%self.offset);
        f.write(struct.pack("B",self.lightType));
        f.write(struct.pack("<f",self.color[0]));
        f.write(struct.pack("<f",self.color[1]));
        f.write(struct.pack("<f",self.color[2]));
        if self.lightType == LampType.POINT or self.lightType == LampType.SPOT:
            f.write(struct.pack("<f",self.range));
        if self.lightType == LampType.SPOT:
            f.write(struct.pack("<f",self.innerAngle));
            f.write(struct.pack("<f",self.outerAngle));
        return;        

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
        
class Animations(Reference):
    def __init__(self):
        self.tipo=ReferenceType.ANIMATIONS;
        self.animations=[];
        return;
    def writeReference(self,f):
        Reference.writeReference(self,f);
        for c in self.animations:
            c.writeReference(f);
        return;
        
    def updateOffset(self,f):
        Reference.updateOffset(self,f);
        for c in self.animations:
            c.updateOffset(f);
        return;
        
    def writeData(self,f):
        self.offset=f.tell();
        f.write(struct.pack("<I",len(self.animations)));
        for a in self.animations:
            a.writeData(f);            
        return ;      
        
        
class Animation(Reference):
               
    def __init__(self):
        self.tipo=ReferenceType.ANIMATION;
        self.idani="";
        self.channels=[];
        return;
            
    def writeData(self,f):
        self.offset=f.tell();
        f.write(struct.pack("<I",len(self.idani)));
        if len(self.idani)>0:
            f.write(bytearray(self.idani,"ascii"));
        f.write(struct.pack("<I",len(self.channels)));
        for a in self.channels:
            a.writeData(f);      
        return ;  
     
        
class AnimationChannel(Reference):
               
    def __init__(self):
        self.tipo=ReferenceType.ANIMATION_CHANNEL;
        self.targetId="";
        self.targetAttribute=17;
        self.keyTimes=[];#uint[]  (milliseconds)
        self.values=[];#                  float[]
        self.tangents_in=[];#float[]
        self.tangents_out=[];#float[]
        self.interpolation=[1];#uint[]
        return;
    def writeData(self,f):
        f.write(struct.pack("<I",len(self.targetId)));
        if len(self.targetId)>0:
            f.write(bytearray(self.targetId,"ascii"));
            
        f.write(struct.pack("<I",self.targetAttribute));
        
        f.write(struct.pack("<I",len(self.keyTimes)));
        for k in self.keyTimes:
            f.write(struct.pack("<I",k));
            
        f.write(struct.pack("<I",len(self.values)));
        for v in self.values:
            f.write(struct.pack("<f",v));
        ##**********************************************
        f.write(struct.pack("<I",0));#tangents_in
        f.write(struct.pack("<I",0));#tangents_out
        f.write(struct.pack("<I",len(self.interpolation)));
        for v in self.interpolation:
            f.write(struct.pack("<I",v));
        return ;         


class ReferenceType:
    SCENE=1;
    NODE=2;
    ANIMATIONS=3;
    ANIMATION=4;
    ANIMATION_CHANNEL=5;
    MODEL=11;
    MESH=34;
    MESHSKIN=36;
    CAMERA=32;
    LIGHT=33; #cesar
    
    


class NodeType:
    NODE = 1,
    JOINT = 2
    
#cesar
class LampType:
    DIRECTIONAL= 1;
    POINT =  2;
    SPOT= 3; 

    



class Exporter(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_gameplay.gpb";
    bl_label        = "Gameplay3d Exporter";
    bl_options      = {'PRESET'};
    filename_ext    = ".gpb";
    objetos=[];
    
    def procesarArmature(self,nodeMesh, mesh):
        bobject=mesh.parent;
        armature = bobject.data;
        nodeMesh.model.meshSkin=MeshSkin();
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
        node.tipoNodo=NodeType.JOINT;
        node.reference=bobject.name;
        self.objetos.append(node);
        huesos={};
        nodeMesh.model.meshSkin.bindShape[0]=1.0;
        nodeMesh.model.meshSkin.bindShape[1]=0.0;
        nodeMesh.model.meshSkin.bindShape[2]=0.0;
        nodeMesh.model.meshSkin.bindShape[3]=0.0;
        
        nodeMesh.model.meshSkin.bindShape[4]=0.0;
        nodeMesh.model.meshSkin.bindShape[5]=1.0;
        nodeMesh.model.meshSkin.bindShape[6]=0.0;
        nodeMesh.model.meshSkin.bindShape[7]=0.0;
        
        nodeMesh.model.meshSkin.bindShape[8]=0.0;
        nodeMesh.model.meshSkin.bindShape[9]=0.0;
        nodeMesh.model.meshSkin.bindShape[10]=1.0;
        nodeMesh.model.meshSkin.bindShape[11]=0.0;
        
        nodeMesh.model.meshSkin.bindShape[12]=0.0;
        nodeMesh.model.meshSkin.bindShape[13]=0.0;
        nodeMesh.model.meshSkin.bindShape[14]=0.0;
        nodeMesh.model.meshSkin.bindShape[15]=1.0;
        
        nodeMesh.model.meshSkin.jointBindPoses=[0]*(len(armature.bones)*16);
        i=0;
        for b in armature.bones:
            bone= Node();
            bone.reference=b.name;
            nodeMesh.model.meshSkin.joints.append(bone);
            bone.transforms[0]=b.matrix_local[0][0];
            bone.transforms[1]=b.matrix_local[1][0];
            bone.transforms[2]=b.matrix_local[2][0];
            bone.transforms[3]=b.matrix_local[3][0];
            bone.transforms[4]=b.matrix_local[0][1];
            bone.transforms[5]=b.matrix_local[1][1];
            bone.transforms[6]=b.matrix_local[2][1];
            bone.transforms[7]=b.matrix_local[3][1];
            bone.transforms[8]=b.matrix_local[0][2];
            bone.transforms[9]=b.matrix_local[1][2];
            bone.transforms[10]=b.matrix_local[2][2];
            bone.transforms[11]=b.matrix_local[3][2];
            bone.transforms[12]=b.matrix_local[0][3];
            bone.transforms[13]=b.matrix_local[1][3];
            bone.transforms[14]=b.matrix_local[2][3];
            bone.transforms[15]=b.matrix_local[3][3];
            nodeMesh.model.meshSkin.jointBindPoses[0+i*16]=b.matrix_local[0][0];
            nodeMesh.model.meshSkin.jointBindPoses[1+i*16]=b.matrix_local[1][0];
            nodeMesh.model.meshSkin.jointBindPoses[2+i*16]=b.matrix_local[2][0];
            nodeMesh.model.meshSkin.jointBindPoses[3+i*16]=b.matrix_local[3][0];
            nodeMesh.model.meshSkin.jointBindPoses[4+i*16]=b.matrix_local[0][1];
            nodeMesh.model.meshSkin.jointBindPoses[5+i*16]=b.matrix_local[1][1];
            nodeMesh.model.meshSkin.jointBindPoses[6+i*16]=b.matrix_local[2][1];
            nodeMesh.model.meshSkin.jointBindPoses[7+i*16]=b.matrix_local[3][1];
            nodeMesh.model.meshSkin.jointBindPoses[8+i*16]=b.matrix_local[0][2];
            nodeMesh.model.meshSkin.jointBindPoses[9+i*16]=b.matrix_local[1][2];
            nodeMesh.model.meshSkin.jointBindPoses[10+i*16]=b.matrix_local[2][2];
            nodeMesh.model.meshSkin.jointBindPoses[11+i*16]=b.matrix_local[3][2];
            nodeMesh.model.meshSkin.jointBindPoses[12+i*16]=b.matrix_local[0][3];
            nodeMesh.model.meshSkin.jointBindPoses[13+i*16]=b.matrix_local[1][3];
            nodeMesh.model.meshSkin.jointBindPoses[14+i*16]=b.matrix_local[2][3];
            nodeMesh.model.meshSkin.jointBindPoses[15+i*16]=b.matrix_local[3][3];
            #****
         
            
            bone.tipoNodo=NodeType.JOINT;
            huesos[bone.reference]=bone;
            i+=1;
            if b.parent is None:
                node.childrens.append(bone);
                #bone.parent_id=node.reference;
                print(bone.parent_id);
            else:
                huesos[b.parent.name].childrens.append(bone);
                bone.parent_id=huesos[b.parent.name].reference;
        return node;

    def procesarAnimation(self,mesh):
        start=bpy.context.scene.frame_start;
        end=bpy.context.scene.frame_end;
        fps=bpy.context.scene.render.fps;
        bobject=mesh.parent;
        ani=Animation();
        ani.idani="animations";
        ani.reference="animations";
        armature = bobject;
        for b in armature.pose.bones:
            channel= AnimationChannel();
            channel.targetId=b.name;
            for i in range(start,end):
                bpy.context.scene.frame_set(i);
                channel.keyTimes.append(round(i*(1000/fps)));
                #print("keyTime : "+str(round(i*(1000/fps))));
                channel.values.append(b.scale[0]);
                channel.values.append(b.scale[1]);
                channel.values.append(b.scale[2]);
                channel.values.append(b.rotation_quaternion[0]);
                channel.values.append(b.rotation_quaternion[1]);
                channel.values.append(b.rotation_quaternion[2]);
                channel.values.append(b.rotation_quaternion[3]);
                channel.values.append(b.location[0]);
                channel.values.append(b.location[1]);
                channel.values.append(b.location[2]);
            ani.channels.append(channel);
        self.animaciones.animations.append(ani);
        
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
        self.objetos.append(node);
        #cesar original: if bobject.parent.type=='ARMATURE':
        #cesar cambio:
        if bobject.parent != None and bobject.parent.type == 'ARMATURE':
            self.procesarArmature(node,bobject);
            self.procesarAnimation(bobject);
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
        
    def procesarLamp(self, lamp):
        bobject=lamp;
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
        node.light=Light();
        node.reference=lamp.name;
        node.light.reference=lamp.name+"light";
        lampdata = lamp.data;
        if lampdata.type == "POINT":
            node.light.lightType = LampType.POINT;
        elif lampdata.type == "SUN":
            node.light.lightType = LampType.DIRECTIONAL;
        elif lampdata.type == "SPOT":
            node.light.lightType = LampType.SPOT;
        else:
            print("ERROR: lamp type not supported");
            return;
        node.light.color[0] = lampdata.color[0];
        node.light.color[2] = lampdata.color[1];
        node.light.color[1] = lampdata.color[2];
        if lampdata.type == "SUN" or lampdata.type == "SPOT":
            node.light.range = lampdata.distance;
        if lampdata.type == "SPOT":
            #spot_size is in radians!
            node.light.innerAngle = lampdata.spot_size;    
            node.light.outerAngle = lampdata.spot_size;
        print("procesando lamp ");
        self.objetos.append(node);
        return node;
        
    def execute(self, context):
        global meshes_to_clear;
        global reference_count;
        reference_count=0;
        meshes_to_clear=[];
        bpy.ops.object.mode_set(mode='OBJECT');
        # Set the default return state to FINISHED
        result = {'FINISHED'};
        # Check that the currently selected object contains mesh data for exporting
        self.objetos=[];
        self.animaciones=Animations();
        self.animaciones.reference="__animations__";
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                self.procesarMesh(ob);
            elif ob.type == 'LAMP':
                self.procesarLamp(ob);
        # Create a file header object with data stored in the body section   
        # Open the file for writing
        camera = self.procesarCamera(bpy.data.cameras[bpy.context.scene.camera.name]);
        self.objetos.append(camera);
        file = open(self.filepath, 'bw');
        file.write(b'\xABGPB\xBB\r\n\x1A\n');
        file.write(struct.pack("B",1));
        file.write(struct.pack("B",2));
        referece_position=file.tell();
        file.write(struct.pack("<I",0));#0 se actualiza luego con el
        scene=Reference();
        scene.tipo=ReferenceType.SCENE;
        scene.reference="__SCENE__";
        scene.writeReference(file);
        for o in  self.objetos:
            o.writeReference(file);
        self.animaciones.writeReference(file);
        scene.offset=file.tell();
        
        file.write(struct.pack("<I",len(self.objetos)));
        for o in  self.objetos:
            o.writeNode(file);
        
#write data of scene
        file.write(struct.pack("<I",len(camera.reference)+1));#camara xref
        file.write(bytearray('#',"ascii"));
        if len(camera.reference)>0:
            file.write(bytearray(camera.reference,"ascii"));
        file.write(struct.pack("<f",1.0));
        file.write(struct.pack("<f",1.0));
        file.write(struct.pack("<f",1.0));
        self.animaciones.writeData(file);
        
        for o in  self.objetos:
            o.writeExtra(file);
        for o in  self.objetos:
            o.updateOffset(file);
        scene.updateOffset(file);
        self.animaciones.updateOffset(file);
        file.seek(referece_position);
        file.write(struct.pack("<I",reference_count));#+1 for scene reference , *2 for node+mesh reference and node+camera reference 
        file.close();
        for m in meshes_to_clear:
            bpy.data.meshes.remove(m);
        return result;

