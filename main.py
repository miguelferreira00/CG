from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

front_rotation = 0.0
back_rotation = 0.0
cam_x, cam_y, cam_z = 0.0, 2.0, 6.0 # initial position
look_x, look_y, look_z = 0.0, -0.5, 0.0 # where to look
cam_radius = 6.0
cam_angle = 0.0

def init():
    glEnable(GL_DEPTH_TEST)       # depth
    glClearColor(0.1, 0.1, 0.1, 1.0)  # background color

def draw_body():
    # Car base
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)   # vermelho para o corpo
    glScalef(3.4, 0.5, 1.8) # scale
    glutSolidCube(1.0)
    glPopMatrix()

    # Car top
    glPushMatrix()
    glColor3f(0.8, 0.0, 0.0)
    glTranslatef(-0.3, 0.5, 0)  
    glScalef(2, 0.7, 1.4) # smaller than base
    glutSolidCube(1.0)
    glPopMatrix()

def draw_wheel(x, y, z, rotate_angle):
    glPushMatrix()
    glTranslatef(x, y, z)      # wheel positione
    glRotatef(rotate_angle, 0, 0, 1)  # wheel rotation

    # tire
    glColor3f(0, 0, 0)   # black color
    glutSolidTorus(0.1, 0.3, 20, 20)  # roda

    # rims
    glColor3f(0.8, 0.8, 0.8) # metalic gray
    glutSolidCone(0.25, 0.05, 20, 20)

    glPopMatrix()


def draw_car():
    draw_body()
    draw_wheel(-1.0, -0.5, 1.0, front_rotation) # left front
    draw_wheel(1.0, -0.5, 1.0, front_rotation) # right front
    draw_wheel(-1.0, -0.5, -1.0, back_rotation) # left back
    draw_wheel(1.0, -0.5, -1.0, back_rotation) # right back

def keyboard(key, x, y):
    global cam_angle
    step = 5
    if key == b'q':
        cam_angle -= step
    elif key == b'e':
        cam_angle += step
    glutPostRedisplay() # redraw the scene

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # convert angle into coords
    cam_x = cam_radius * math.sin(math.radians(cam_angle))
    cam_z = cam_radius * math.cos(math.radians(cam_angle))

    # Câmara
    gluLookAt(cam_x, cam_y, cam_z,   # cam position
              look_x, look_y, look_z,   # where to look
              0, 1, 0)   # vetor "up"

    # draw a simple cube
    draw_car()

    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, w / float(h or 1), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# window setup
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 600)
glutCreateWindow(b"CG - Grupo 35")

init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutReshapeFunc(reshape)
glutMainLoop()
