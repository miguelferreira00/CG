from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import numpy as np
from PIL import Image


front_rotation = 0.0
back_rotation = 0.0
cam_x, cam_y, cam_z = 0.0, 2.0, 6.0 # initial position
look_x, look_y, look_z = 0.0, -0.5, 0.0 # where to look
cam_radius = 6.0
cam_angle = 0.0
car_x, car_z = 0.0, 0.0
car_angle = 0.0
wheel_angle = 0.0
speed = 0.0
acceleration = 0.02
friction = 0.98
texture_ground = None


def init():
    global texture_ground

    glEnable(GL_DEPTH_TEST)       # depth
    glClearColor(0.5, 0.7, 1.0, 1.0)  # background color
    glEnable(GL_TEXTURE_2D)   

    texture_ground = load_texture("texture_ground.jpg")

def draw_ground():
    glBindTexture(GL_TEXTURE_2D, texture_ground)

    tile_repeat = 35  # how many times the texture repeats across the floor size

    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)

    glTexCoord2f(0, 0)
    glVertex3f(-50, -0.51, -50)

    glTexCoord2f(tile_repeat, 0)
    glVertex3f(50, -0.51, -50)

    glTexCoord2f(tile_repeat, tile_repeat)
    glVertex3f(50, -0.51, 50)

    glTexCoord2f(0, tile_repeat)
    glVertex3f(-50, -0.51, 50)

    glEnd()


def draw_body():
    # Fundo (paralelepípedo achatado)
    glPushMatrix()
    glColor3f(0.6, 0.6, 0.6)
    glTranslatef(0.0, -0.5, 0.0)   # centro no chão
    glScalef(2.0, 0.1, 4.0)        # largura X, espessura Y, comprimento Z
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede esquerda
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(-1.0, -0.25, 0.0) # posição à esquerda
    glScalef(0.1, 0.5, 4.0)        # espessura X, altura Y, comprimento Z
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede direita
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(1.0, -0.25, 0.0)  # posição à direita
    glScalef(0.1, 0.5, 4.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede frente
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(0.0, -0.25, 2.0)  # posição à frente
    glScalef(2.0, 0.5, 0.1)        # largura X, altura Y, espessura Z
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede trás
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(0.0, -0.25, -2.0) # posição atrás
    glScalef(2.0, 0.5, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    # motor
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)          # vermelho
    glTranslatef(0.0, -0.25, 1.3)     # centro no meio da banheira
    glScalef(2, 0.5, 1.5)           # ocupa menos de metade da altura e quase todo o comprimento
    glutSolidCube(1.0)
    glPopMatrix()


    # Car top
    # glPushMatrix()
    # glColor3f(0.8, 0.0, 0.0)
    # glTranslatef(-0.3, 0.5, 0)  
    # glScalef(2, 0.7, 1.4) # smaller than base
    # glutSolidCube(1.0)
    # glPopMatrix()


def load_texture(path):
    img = Image.open(path)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)  # OpenGL reads upside-down
    img_data = img.convert("RGB").tobytes()

    width, height = img.size

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    # carregar textura
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                 width, height, 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)

    # parâmetros da textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    return tex_id

def draw_wheel(x, y, z, rotate_angle, side):
    glPushMatrix()
    glTranslatef(x, y, z)

    # alinhar roda vertical
    glRotatef(90, 0, 1, 0)

    # orientação tangente à base
    if side == "left":
        glRotatef(180, 0, 1, 0)   # roda da esquerda aponta para fora
    # roda da direita não precisa (já aponta para fora)

    # rotação de rolamento (andar)
    glRotatef(rotate_angle, 1, 0, 0)

    # pneu
    glColor3f(0, 0, 0)
    glutSolidTorus(0.1, 0.3, 20, 20)

    # jante
    glColor3f(0.8, 0.8, 0.8)
    glutSolidCone(0.25, 0.05, 20, 20)

    glPopMatrix()

def draw_seat(x, y, z):
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)        # vermelho para destacar
    glTranslatef(x, y, z)           # posição do banco
    glScalef(0.6, 0.4, 0.6)         # largura, altura, profundidade
    glutSolidCube(1.0)
    glPopMatrix()

def draw_steering_wheel(x, y, z):
    glPushMatrix()
    glRotatef(180, 1, 0, 0)

    # Aro do volante (torus mais pequeno)
    glColor3f(0.0, 0.0, 0.0)
    glutSolidTorus(0.04, 0.3, 30, 30)   # antes 0.05, 0.4 → reduzido

    # Miolo central (esfera menor)
    glColor3f(0.8, 0.0, 0.0)
    glutSolidSphere(0.08, 20, 20)       # antes 0.1 → reduzido

    # Raios (ajustados para o novo tamanho)
    glColor3f(0.8, 0.8, 0.8)
    for angle in [0, 120, 240]:
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(0.20, 0.0, 0.0)    # antes 0.25 → mais perto do centro
        glScalef(0.2, 0.05, 0.05)       # ligeiramente menor
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()



def draw_car():
    glPushMatrix()
    glTranslatef(car_x, 0.5, car_z)
    glRotatef(car_angle, 0, 1, 0)

    draw_body()
    
    # wheels
    draw_wheel(-1.1, -0.5, 1.0, front_rotation, "left") # left front
    draw_wheel(1.1, -0.5, 1.0, front_rotation, "right") # right front
    draw_wheel(-1.1, -0.5, -1.0, back_rotation, "left") # left back
    draw_wheel(1.1, -0.5, -1.0, back_rotation, "right") # right back

     # front seats
    draw_seat(-0.5, -0.25, -0.3)   # left seat
    draw_seat( 0.5, -0.25, -0.3)   # right seat

    # back seats
    draw_seat(-0.5, -0.25, -1.3)  # left back seat
    draw_seat( 0.5, -0.25, -1.3)  # left back seat


    # steering wheel
    glPushMatrix()
    glTranslatef(-0.5, -0.15, 0.5)      # posição no carro
    glRotatef(wheel_angle, 0, 0, 1)     # aplica rotação do volante sobre Y
    draw_steering_wheel(0, 0, 0)        # desenha volante local
    glPopMatrix()

    glPopMatrix()


def keyboard(key, x, y):
    global cam_angle, wheel_angle, speed
    turn = 5

    if key == b'w': # front
        speed += acceleration
        speed = min(speed, 0.2)
    elif key == b's': # back
        speed -= acceleration
        speed = max(-0.1, speed)    
    elif key == b'a': # left
        wheel_angle = max(-45, wheel_angle - turn) #steering wheel turns max 45°
    elif key == b'd': # right
        wheel_angle = min(45, wheel_angle + turn)
    elif key == b'q':
        cam_angle -= turn
    elif key == b'e':
        cam_angle += turn

    glutPostRedisplay() # redraw the scene

def display():
    global wheel_angle, cam_x, cam_z, car_angle, speed, car_x, car_z
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    speed *= friction
    if abs(speed) < 0.001:
        speed = 0

    car_angle += (speed * wheel_angle) / 50.0
    

    # update position
    car_x += speed * math.sin(math.radians(car_angle))
    car_z += speed * math.cos(math.radians(car_angle))

    #car position
    target_x, target_y, target_z = car_x, 0.0, car_z
    distance = 6.0 # distance to the car
    height = 2.0 # cam height

    # convert angle into coords
    cam_x = target_x - distance * math.sin(math.radians(car_angle))
    cam_z = target_z - distance * math.cos(math.radians(car_angle))
    cam_y = height


    # Câmara
    gluLookAt(cam_x, cam_y, cam_z,
          target_x, target_y, target_z,
          0, 1, 0)

    draw_ground()  # draw the ground plane
    # draw a simple cube
    draw_car()


    if wheel_angle > 0:
        wheel_angle -= 1
    elif wheel_angle < 0:
        wheel_angle += 1

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
