from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from PIL import Image
import numpy as np
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape

from panda3d.bullet import BulletDebugNode
from pandac.PandaModules import GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles, Geom, GeomNode, NodePath, GeomPoints
"""
from panda3d.core import loadPrcFileData
loadPrcFileData("", "window-type offscreen" ) # Spawn an offscreen buffer
loadPrcFileData("", "audio-library-name null" ) # Prevent ALSA errors
from direct.showbase.ShowBase import ShowBase
#import direct.directbase.DirectStart


base = ShowBase()
base.scene = base.loader.loadModel("input.obj")
base.scene.reparentTo(base.render)
 # Apply scale and position transforms on the model.
base.scene.setScale(0.25, 0.25, 0.25)
base.scene.setPos(-1, 1, 0)
base.graphicsEngine.renderFrame()
base.screenshot(namePrefix='screenshot.png', defaultFilename=0, source=None, imageComment="")

img = Image.open('screenshot.png')
img_resize = img.resize((128, 64))
#img_resize = img_resize.crop((0, 0, 100, 64))
img_resize.save('screenshot.png')
"""
loadPrcFileData("", "win-size 1066 600")


world = BulletWorld()
world.setGravity(Vec3(0, 9.81, 0))

# Update
def update(task):
  dt = globalClock.getDt()
  world.doPhysics(dt)
  return task.cont

def build_bullet_from_model(modelNP):
    body = BulletRigidBodyNode('...')
    for geomNP in modelNP.findAllMatches('**/+GeomNode'):
        geomNode = geomNP.node()
        ts = geomNode.getTransform()
        for geom in geomNode.getGeoms():
          mesh = BulletTriangleMesh()
          mesh.addGeom(geom)

          shape = BulletTriangleMeshShape(mesh, dynamic=False)
          body.addShape(shape, ts)
    return body


class BoxMaker:
    def __init__(self,w,h,d):
        # self.smooth = True/False
        # self.uv = True/False or Spherical/Box/...
        # self.color = Method1/Method2/...
        # self.subdivide = 0/1/2/...
        self.w = w
        self.h = h
        self.d = d

    def generate(self):
        format = GeomVertexFormat.getV3()
        data = GeomVertexData("Data", format, Geom.UHStatic)
        vertices = GeomVertexWriter(data, "vertex")

        vertices.addData3f(-self.w, -self.h, -self.d)
        vertices.addData3f(+self.w, -self.h, -self.d)
        vertices.addData3f(-self.w, +self.h, -self.d)
        vertices.addData3f(+self.w, +self.h, -self.d)
        vertices.addData3f(-self.w, -self.h, +self.d)
        vertices.addData3f(+self.w, -self.h, +self.d)
        vertices.addData3f(-self.w, +self.h, +self.d)
        vertices.addData3f(+self.w, +self.h, +self.d)

        triangles = GeomTriangles(Geom.UHStatic)

        def addQuad(v0, v1, v2, v3):
            triangles.addVertices(v0, v1, v2)
            triangles.addVertices(v0, v2, v3)
            triangles.closePrimitive()

        addQuad(4, 5, 7, 6) # Z+
        addQuad(0, 2, 3, 1) # Z-
        addQuad(3, 7, 5, 1) # X+
        addQuad(4, 6, 2, 0) # X-
        addQuad(2, 6, 7, 3) # Y+
        addQuad(0, 1, 5, 4) # Y+

        geom = Geom(data)
        geom.addPrimitive(triangles)

        node = GeomNode("BoxMaker")
        node.addGeom(geom)

        return NodePath(node)

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)
 
        # Load the environment model.
        self.scene = self.loader.loadModel("input.obj")
        self.setBackgroundColor(0.0,0.0,0.0)

        plight = PointLight('plight')
        plight.setColor(VBase4(0.7, 0.7, 0.7, 1))
        plnp = self.render.attachNewNode(plight)
        plnp.setPos(0, 20, 0)
        self.render.setLight(plnp)

        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.1, 0.1, 0.1, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)

        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(0.8, 0.8, 0.8, 1))
        dlnp = render.attachNewNode(dlight)
        dlnp.setHpr(0, 10, 0)
        self.render.setLight(dlnp)

        # Reparent the model to render.
        shape = BulletBoxShape(Vec3(0.06, 0.12, 0.04))
        node = BulletRigidBodyNode('Box')
        node.setMass(0.6)
        node.addShape(shape)
        boxnode = self.render.attachNewNode(node)
        #boxnode.setHpr(90,90,90)   #or whatever you want to rotate to
        #model = self.loader.loadModel('models/box.egg')
        customBox = BoxMaker(0.06, 0.12, 0.04).generate()
        customBox.setColor(0.97, 0.99, 0.75)
        #customBox.flattenLight()
        customBox.reparentTo(boxnode)
        
        #model.reparentTo(boxnode)
        boxnode.setPos(-0.1, 1.5, 0.65)
        boxnode.setHpr(90,90,90)
        #model.reparentTo(self.scene)
        #model.setPos(0, 0.0, 0.0)
        #boxnode.reparentTo(self.render)

        bin_node = build_bullet_from_model(self.scene)
        bin_shape_node = self.render.attachNewNode(bin_node)
        self.scene.reparentTo(bin_shape_node)
        bin_shape_node.setPos(0, 2.4, 0.2)
        bin_shape_node.setHpr(90,90,90)   #or whatever you want to rotate to
        
        #self.scene.setPos(0, 5.5, 0.2)
        #bin_node.setHpr(90,90,90)   #or whatever you want to rotate to
        world.attachRigidBody(bin_node)
        world.attachRigidBody(node)

        #shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
        #node = BulletRigidBodyNode('Ground')
        #node.addShape(shape)
        #np = self.render.attachNewNode(node)
        #np.setPos(0, 7.0, 0.0)
        #np.setHpr(90,90,90)
        #world.attachRigidBody(node)

        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(False)
        debugNode.showNormals(False)
        debugNP = self.render.attachNewNode(debugNode)
        debugNP.show()
        world.setDebugNode(debugNP.node())

        #self.scene.reparentTo(self.render)
        self.taskMgr.add(update, 'update')

        #self.disableMouse()




app = MyApp()
app.run()