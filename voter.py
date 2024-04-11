import numpy
import numpy.random
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

### Animation
class HeadShaking:
    def __init__(self, speed):
        self.ratio = 0.0
        self.speed = speed

    def update(self):
        self.ratio += self.speed
        if self.ratio >= 1.0 or self.ratio <= 0.0:
            self.speed = -self.speed


class Model:
    def _draw(self):
        pass

    def render(self):
        glPushMatrix()
        self._draw()
        glPopMatrix()

    def update(self):
        pass

### Model, Human having 2 different (Blue and Red) flags.
class Voter(Model):
    def __init__(self, pos, scale):
        self.pos_x, self.pos_y, self.pos_z = pos
        self.scale_x, self.scale_y, self.scale_z = scale
        self.jump = 0.0
        self.head = Head()
        self.body = Body()

    def _draw(self):
        glTranslate(self.pos_x, self.pos_y, self.pos_z)
        glTranslate(0.0, self.jump, 0)
        glScale(self.scale_x, self.scale_y, self.scale_z)
        self.head.render()
        self.body.render()

    def update(self):
        self.head.update()
        self.body.update()
    
class Head(Model):

    def __init__(self):
        self.degree = 0.0
        self.animation = HeadShaking(0.02)
        self.animation.ratio = 0.5

    def _draw(self):
        glColor(0.98, 0.81, 0.69)
        glRotate(self.degree, 0.0, 0.0, 1.0)
        glutSolidSphere(1.0, 32, 32)
        
        glPushMatrix()
        # define left eye 
        glColor3f(0.0, 0.0, 0.0)  # black color 
        glTranslatef(-0.3, 0.2, 0.9)  
        glutSolidSphere(0.1, 10, 10) 
        glPopMatrix()

        # define right eye 
        glPushMatrix()
        glTranslatef(0.3, 0.2, 0.9) 
        glutSolidSphere(0.1, 10, 10) 
        glPopMatrix()
        
        ## define hair 
        glColor3f(0.5, 0.25, 0.0)  # brown 
        glPushMatrix()
        glTranslatef(0.0, 0.3, 0.0) 
        ## define clipping plane, to express hair (up-half)
        clip_plane = (0.0, 0.2, 0.0, 0.0)
        glEnable(GL_CLIP_PLANE0)
        glClipPlane(GL_CLIP_PLANE0, clip_plane)
        glutSolidSphere(1.03, 32, 32) 
        glDisable(GL_CLIP_PLANE0)
        glPopMatrix()

    def update(self):
        self.degree = (self.animation.ratio - 0.5) * 20.0
        self.animation.update()
  
### Body
class Body(Model):
    def __init__(self):
        self.left_arm = Arm(-90, -1.5, (0.0, 0.0, 1.0)) # define left arm, begin with -90 degree.
        self.right_arm = Arm(-90, 1.5, (1.0, 0.0, 0.0)) # define right arm, begin with -90 degree.
        self.left_leg = Leg(0, -0.8)
        self.right_leg = Leg(0, 0.8)
    
    def _draw(self):
        glColor(0.7, 0.7, 0.7) # gray color 
        glTranslate(0.0, -1.5, 0.0)
        glutSolidCube(2) # body is 2x2x2 solid cube. 
        self.left_arm.render()
        self.right_arm.render()
        self.left_leg.render()
        self.right_leg.render()
        
    def update(self):
        self.left_arm.update()
        self.right_arm.update()
        self.left_leg.update()
        self.right_leg.update()
    
### Arm
class Arm(Model):
    def __init__(self, degree, displacement, color):
        self.degree = degree
        self.displacement = displacement
        self.node = ArmNode(ArmNode(FlagNode(color))) # last node is flag, colored RED or BLUE. 

    def _draw(self):
        glTranslate(0.0, 0.5, 0.0) 
        glTranslate(self.displacement, 0.0, -1.0)
        glRotate(self.degree, 1.0, 0.0, 0.0)  # express each arm's movement 
        self.node.render()

    def update(self):
        self.node.update()
    
    
### Arm Node, Each arm consists of two ArmNode and one FlagNode.
class ArmNode(Model):

    def __init__(self, next_node=None):
        self.flag = None
        self.next_node = None
        if isinstance(next_node, FlagNode):
            self.flag = next_node
        else:
            self.next_node = next_node

    def _draw(self):
        if self.next_node: # If inner one (express arm with T-Shirts)
            glColor(0.7, 0.7, 0.7)
            glTranslate(0.0, 0.1, 0.0)
            glutSolidCube(0.5) 
            glTranslate(0.0, -0.5, 0.0)
            glutSolidCube(0.5)
            glTranslate(0.0, -0.5, 0.0) 
        elif self.flag: # If outer one (express hands)
            glColor(0.7, 0.7, 0.7)
            glTranslate(0.0, 0.1, 0.0)
            glutSolidCube(0.5) 
            glTranslate(0.0, -0.5, 0.0)
            glColor(0.98, 0.81, 0.69)
            glutSolidCube(0.5)
            glTranslate(0.0, -0.5, 0.0)
        if self.next_node:
            self.next_node.render()
        elif self.flag:
            self.flag.render()

    def update(self):
        if self.next_node:
            self.next_node.update()
      
class FlagNode(Model):

    def __init__(self, color):
        self.R, self.G, self.B = color

    def _draw(self):
        glColor3f(self.R, self.G, self.B)
        width, height = 2.0, 1.0  # width and height of flag
        
        glBegin(GL_QUADS) # start to draw 
        if self.R != 0:
            glVertex3f(0, 0, 0)  
            glVertex3f(0, -height, 0)  
            glVertex3f(width, -height, 0)  
            glVertex3f(width, 0, 0)  
        elif self.B != 0:
            glVertex3f(0, 0, 0)  
            glVertex3f(0, -height, 0) 
            glVertex3f(-width, -height, 0) 
            glVertex3f(-width, 0, 0)  
        glEnd() # end to draw
    
    def update(self):
        pass    
      
       
### Leg 
class Leg(Model):
    def __init__(self, degree, displacement):
        self.degree = degree
        self.displacement = displacement
        self.node = LegNode(LegNode())

    def _draw(self):
        glTranslate(0.0, -1.5, -1.0) 
        glTranslate(self.displacement, 0.0, 0.0)
        glRotate(self.degree, 0.0, 0.0, 1.0)
        self.node.render()

    def update(self):
        self.node.update()
    
### Leg Node, Each leg consists of two LegNodes.  
class LegNode(Model):
    def __init__(self, next_node=None):
        self.next_node = next_node

    def _draw(self):
        if self.next_node: # If inner one, expresses leg with pants. 
            glColor(0.7, 0.7, 0.7)
            glTranslate(0.0, 0.0, 0.0)
            glutSolidCube(0.7) 
            glTranslate(0.0, -0.7, 0.0)
            glutSolidCube(0.7)
            glTranslate(0.0, -0.7, 0.0)
            
        else: # If outer one 
            glColor(0.7, 0.7, 0.7)
            glTranslate(0.0, 0.0, 0.0)
            glutSolidCube(0.7) 
            glTranslate(0.0, -0.7, 0.0)
            glColor(0.5, 0.5, 0.5) # expresses shoes
            glutSolidCube(0.7) 
            glTranslate(0.0, -0.7, 0.0)
    
        if self.next_node:
            self.next_node.render()

    def update(self):
        if self.next_node:
            self.next_node.update()
        
