
import bpy, math
from mathutils import Vector, Euler, Quaternion, Matrix
sc=bpy.context.scene
rig=bpy.data.objects['FPS_Rig']
def cam(name,loc,tgt,fov=40):
    o=bpy.data.objects.get(name)
    if not o:
        d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); sc.collection.objects.link(o)
    o.data.lens_unit='FOV'; o.data.sensor_fit='VERTICAL'; o.data.angle=math.radians(fov); o.data.clip_start=0.005
    o.location=loc; d=(Vector(tgt)-Vector(loc)); o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    return o
def setcams(c):
    c=Vector(c)
    cam('CR',c+Vector((-0.40,0.02,0.06)),c,36)
    cam('CL',c+Vector((0.40,0.02,0.06)),c,36)
    cam('CT',c+Vector((0.0,0.22,0.30)),c,36)
    cam('CF',c+Vector((-0.12,-0.42,-0.06)),c,36)
def render(prefix):
    for n in ['TmpCam','CR','CL','CT','CF']:
        sc.camera=bpy.data.objects[n]; sc.render.filepath="C:\\Users\\PC\\Desktop\\blender\\shots\\%s_%s.png"%(prefix,n)
        if n=='TmpCam': sc.render.resolution_x=960; sc.render.resolution_y=540
        else: sc.render.resolution_x=640; sc.render.resolution_y=480
        bpy.ops.render.render(write_still=True)
    sc.camera=bpy.data.objects['TmpCam']
FING=['Index','Middle','Ring','Pinky']
def pb(n): return rig.pose.bones[n]
def setrot(name, e):
    p=pb(name); p.rotation_mode='XYZ'; p.rotation_euler=Euler([math.radians(a) for a in e],'XYZ')
def hand(side, fingers=None, thumb=None, spread=None):
    s='Right' if side=='R' else 'Left'
    if fingers:
        for f,(a,b,c) in zip(FING,fingers):
            sp=(spread or {}).get(f,0)
            setrot('mixamorig:%sHand%s1'%(s,f),(a,0,sp)); setrot('mixamorig:%sHand%s2'%(s,f),(b,0,0)); setrot('mixamorig:%sHand%s3'%(s,f),(c,0,0))
    if thumb:
        for k,e in enumerate(thumb): setrot('mixamorig:%sHandThumb%d'%(s,k+1),e)

def gunpose(o, rx=0, ry=0, rz=0):
    g=bpy.data.objects['FA M9T']; p=rig.pose.bones['gun_ctrl']
    gunRest=bpy.app.driver_namespace['REST_GUN']; gcRest=rig.data.bones['gun_ctrl'].matrix_local
    R=Matrix.Rotation(math.radians(rz),4,'Z')@Matrix.Rotation(math.radians(ry),4,'Y')@Matrix.Rotation(math.radians(rx),4,'X')@Matrix.Rotation(math.pi,4,'Z')
    T=Matrix.Translation(Vector(o))@R
    p.matrix=T@gunRest.inverted()@gcRest
    bpy.context.view_layer.update()
def grip(trigger=False):
    hand('R',fingers=[(45,45,25) if trigger else (8,8,5),(65,85,50),(70,85,50),(70,80,45)],thumb=[(-15,0,40),(0,0,10),(0,0,10)])
    hand('L',fingers=[(70,80,50),(75,85,55),(78,85,55),(75,80,50)],thumb=[(30,0,-10),(0,0,0),(0,0,0)])

PH={'R':Vector((-0.56,0,0.83)).normalized(),'L':Vector((0.45,0,-0.9)).normalized()}
def basis(y,p):
    y=y.normalized(); p=(p-y*p.dot(y)).normalized(); z=y.cross(p)
    return Matrix((y,p,z)).transposed()
def gunrest():
    v=list(rig['gun_rest']); return Matrix([v[0:4],v[4:8],v[8:12],v[12:16]])
def set_grip(spec):
    G=gunrest(); G3=G.to_3x3().normalized()
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    eb=rig.data.edit_bones
    for s,sp in spec.items():
        Dw=G3@sp['d']; Pw=G3@sp['p']
        R=basis(Dw,Pw)@basis(Vector((0,1,0)),PH[s]).inverted()
        c=eb['IK_hand_'+s]; c.head=G@sp['w']; c.tail=c.head+R@Vector((0,0.08,0)); c.align_roll(R@Vector((0,0,1)))
    bpy.ops.object.mode_set(mode='POSE')
def tilt(deg): 
    r=math.radians(deg); return Vector((0,math.cos(r),-math.sin(r)))
