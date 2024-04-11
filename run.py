### import libraries
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import time
import voter # Hierarchical model 
import pygame # for playing music 

### define global variables
model = None
view_angle = 0.0
robot_jump = False
y_pos = 0.0
leg_degree = 0.0
jump_start_time = 0.0
current_music_file = None  


### Function to draw ground below the model 
def draw_ground():
    glPushMatrix()
    glTranslatef(0.0, -5.8, 0.0)
    glBegin(GL_QUADS)  
    glColor3f(0.96, 0.87, 0.70)  
    glVertex3f(-10.0, 0.0, -10.0) 
    glVertex3f(-10.0, 0.0, 10.0) 
    glVertex3f(10.0, 0.0, 10.0)  
    glVertex3f(10.0, 0.0, -10.0)  
    glEnd()  
    glPopMatrix()


### Function to define the variable associated with model's state
def start_jump():
    global robot_jump, jump_start_time
    if not robot_jump: # start jump just in the case not on jumping already
        robot_jump = True
        jump_start_time = time.time()

### Function to update the model's state 
def update_jump():
    global robot_jump, y_pos, leg_degree, jump_start_time
    if robot_jump:
        t = time.time() - jump_start_time # calculate elapsed time
        y_pos = 0 + 5*t - 0.5*9.81*t**2 # calculate current position with gravity acceleration
        # Adjust degree based on jump phase
        if t <= 0.5:  # Ascending phase
            leg_degree = 30 * t  # Legs separate up to 30 degrees
        elif t > 0.5 and y_pos > 0:  # Descending phase but above ground
            leg_degree = 30 - (30 * (t - 0.5))  # Legs come back together
        else:  # Reset conditions when on ground
            leg_degree = 0
        if y_pos <= 0: # If the model reaches to ground, then terminate the jump state.
            y_pos = 0
            leg_degree = 0
            robot_jump = False
            
            
### Function to play music, related with model's arm position 
def play_music(file_path):
    global current_music_file
    if current_music_file == file_path and pygame.mixer.music.get_busy():
        return
    pygame.mixer.music.stop()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    current_music_file = file_path
    
### Function to take keyboard input and update model's movement
def movement(key, x, y):
    global view_angle
    global model
    
    if key == b'a':  # rotate the viewpoint as C.W.
        view_angle -= 2.0
        
    if key == b'd': # rotate the viewpoint as C.C.W.
        view_angle += 2.0
        
    if key == b'w': # raise up the left arm and down the right arm 
        model.body.left_arm.degree += 5.0
        model.body.right_arm.degree -= 5.0
        
    if key == b's': # raise up the right arm and down the left arm 
        model.body.left_arm.degree -= 5.0
        model.body.right_arm.degree += 5.0             
        
    if key == b'j': # make the model jump
        start_jump()

    if model.body.left_arm.degree < -180:  # Constraint about model's left arm
        model.body.left_arm.degree = -180
    if model.body.left_arm.degree > 0: 
        model.body.left_arm.degree = 0 
    if model.body.right_arm.degree < -180:  # Constraint about model's right arm
        model.body.right_arm.degree = -180
    if model.body.right_arm.degree > 0:  
        model.body.right_arm.degree = 0 
        
    music_file = None
    if model.body.right_arm.degree > model.body.left_arm.degree: # For the case right arm is up. 
        music_file = "music/music_1.mp3" # music about, 'opposite party'
    elif model.body.right_arm.degree < model.body.left_arm.degree: # For the case left arm is up. 
        music_file = "music/music_2.mp3" # music about, 'ruling party'
    else: # For the case, in neutrality. 
        music_file = None
        pygame.mixer.music.stop()
    if music_file:
        # play music with pygame.mixer, without additional thread 
        play_music(music_file)
        
    model.body.left_arm.update()
    model.body.right_arm.update()
    glutPostRedisplay()

def display():
    global view_angle
    global y_pos
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    update_jump()
    
    # Set the camera position 
    gluLookAt(0.0, 0.0, 1.0, # camera position 
              0.0, 0.0, 0.0, # viewpoint poision 
              0.0, 1.0, 0.0) # camera's view direction 
    
    draw_ground()  # draw a ground

    # rotation manipulated by Keyboard's A key and D key
    glRotatef(view_angle, 0, 1, 0) # viewpoint rotation along y-axis
    model.pos_y = y_pos
    model.body.left_leg.degree = -leg_degree
    model.body.right_leg.degree = leg_degree
    model.update()
    model.render()
    glutSwapBuffers()
    return

def init():
    glClearDepth(1.0)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (1.0, 1.0, 1.0, 1.0))
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)

    glMatrixMode(GL_PROJECTION)
    glFrustum(-1.0, 1.0, -1.0, 1.0, 1.0, 30)

    glMatrixMode(GL_MODELVIEW)

def makeModel():
    global model
    pos = (0.0, 0.0, -6.0)
    scale = (1.0, 1.0, 1.0)
    model = voter.Voter(pos, scale)


if __name__ == "__main__":
    glutInit()
    glutInitWindowPosition(100, 100)
    glutInitWindowSize(600, 600)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutCreateWindow('2024S SNU Computer Graphics PA1 - Ruling Party and Opposition Party:)')
    pygame.mixer.init()
    init()
    makeModel()
    glutDisplayFunc(display)
    glutKeyboardFunc(movement)
    
    glutMainLoop()
