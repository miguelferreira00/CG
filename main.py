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
car_x, car_y, car_z = 0.0, 0.5, 0.0
car_angle = 0.0
wheel_rotation = 0.0
wheel_angle = 0.0
speed = 0.0
acceleration = 0.02
friction = 0.98

car_left_door_angle = 90.0
car_right_door_angle = 90.0
car_left_door_closing = False
car_left_door_opening = False
car_right_door_closing = False
car_right_door_opening = False

texture_ground = None
texture_door = None


garage_x, garage_z = 0, 30
garage_door_angle = 0
door_opening = False
door_closing = False


walls_loaded = False
door_loaded = False
walls_vertices, walls_faces = [], []
door_vertices, door_faces = [], []


def init():
    global texture_ground, walls_loaded, door_loaded
    global walls_vertices, walls_faces, door_vertices, door_faces
    global texture_door 
   

    glEnable(GL_DEPTH_TEST)       # depth
    glClearColor(0.5, 0.7, 1.0, 1.0)  # background color
    glEnable(GL_TEXTURE_2D)   

    texture_ground = load_texture("texture_ground.jpg")
    texture_door = load_texture("door_text.jpg")

    walls_vertices, walls_faces = load_obj_file("garage.obj")   
    door_vertices, door_faces = load_obj_file("door.obj") 

    if walls_vertices:
        walls_loaded = True
    if door_vertices:
        door_loaded = True 


def draw_garage_walls():
   
    if not walls_loaded:
        return
    
    glPushMatrix()
    glTranslatef(garage_x, 0, garage_z)
    
    
    glScalef(1, 1, 1)  
    
    #cor das paredes
    glColor3f(0.7, 0.7, 0.7)  # cinzento claro
    
    # faces
    for face in walls_faces:
        if len(face) >= 3:
            glBegin(GL_POLYGON)
            for vertex_idx in face:
                if vertex_idx < len(walls_vertices):
                    glVertex3fv(walls_vertices[vertex_idx])
            glEnd()
    
    glPopMatrix()


def draw_garage_door():
 
    if not door_loaded:
        return
    
    glPushMatrix()
    glTranslatef(garage_x, 0, garage_z)
    glScalef(1, 1, 1)
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_door)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glColor3f(1, 1, 1)
    
    if door_vertices:
        min_y = min(v[1] for v in door_vertices)
        max_y = max(v[1] for v in door_vertices)
        min_x = min(v[0] for v in door_vertices)
        max_x = max(v[0] for v in door_vertices)
        
        door_height = max_y - min_y
        ceiling_y = 3.7
        
        # para de rolar para cime quando atingir o teto
        max_rollup = ceiling_y - min_y  # Maximo 
        rollup_amount = min(
            (garage_door_angle / 90.0) * door_height,
            max_rollup
        )
        
        for face in door_faces:
            if len(face) >= 3:
                glBegin(GL_POLYGON)
                for vertex_idx in face:
                    if vertex_idx < len(door_vertices):
                        x, y, z = door_vertices[vertex_idx]
                        
                        cutoff_y = min_y + rollup_amount
                        
                        if y < cutoff_y:
                            y_transformed = y + rollup_amount
                        else:
                            y_transformed = y
                        
                        u = (x - min_x) / (max_x - min_x)
                        v = (y - min_y) / door_height
                        glTexCoord2f(u, v)
                        glVertex3f(x, y_transformed, z)
                glEnd()
    
    glBindTexture(GL_TEXTURE_2D, texture_ground)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    glPopMatrix()

def draw_garage_switch():
    glPushMatrix()
    glTranslatef(garage_x, 0, garage_z)
    
    glDisable(GL_TEXTURE_2D)
    
    # no centro, por cima da porta 
    light_x = 0.0        
    light_y = 4        
    light_z = -8.2      
    
    # Color: vermelho se porta fechada, verde se aberta
    if garage_door_angle < 49:  # fechada ou quase
        r, g, b = 1.0, 0.0, 0.0  # RED
    else:  # aberta
        r, g, b = 0.0, 1.0, 0.0  # GREEN
    
    #luz 
    glColor3f(r, g, b)
    glPushMatrix()
    glTranslatef(light_x, light_y, light_z) 
    glutSolidSphere(0.08, 12, 12)
    
    # brilho
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(r, g, b, 0.2)
    glutSolidSphere(0.15, 12, 12)

    
    glDisable(GL_BLEND)
    glPopMatrix()
    glEnable(GL_TEXTURE_2D)
    glPopMatrix()


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
    

    # Parede direita (atras da porta)
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(-1.0, -0.25, -1.3) # posição depois da porta direita
    glScalef(0.1, 0.5, 1.3)       # espessura X, altura Y, comprimento Z
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede direita (a frente da porta)
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(-1.0, -0.25, 0.4) # posição antes da porta direita
    glScalef(0.1, 0.5, 0.5)        # espessura X, altura Y, comprimento Z
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede esquerda (atras da porta)
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(1.0, -0.25, -1.3)  # posição depois da porta esquerda
    glScalef(0.1, 0.5, 1.3)
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede esquerda (a frente da porta)
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glTranslatef(1.0, -0.25,0.4)  # posição depois da porta esquerda
    glScalef(0.1, 0.5, 0.5)
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

def load_obj_file(filename):
    #carregar os vertices do obje file
    vertices = []
    faces = []
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Ignorar comentários e outros elementos 
                if line.startswith('#') or line.startswith('mtllib') or line.startswith('usemtl'):
                    continue
                
                # Vertex: "v x y z"
                if line.startswith('v '):
                    parts = line.split()
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append([x, y, z])
                
                # Face: "f v1/vt1/vn1 v2/vt2/vn2 ..."
                elif line.startswith('f '):
                    parts = line.split()
                    face = []
                    for i in range(1, len(parts)):  
                        vertex_idx = int(parts[i].split('/')[0]) - 1  
                        face.append(vertex_idx)
                    faces.append(face)
        
        print(f" Loaded {filename}: {len(vertices)} vertices, {len(faces)} faces")
        return vertices, faces
        
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None, None

def draw_wheel(x, y, z, rotate_angle, side, is_back=False):
    glPushMatrix()
    glTranslatef(x, y, z)

    # alinhar roda vertical
    glRotatef(90, 0, 1, 0)

    if is_back:
        glScalef(1.2, 1.2, 1.2)  # rodas traseiras maiores

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


    #porta esquerda 
    glPushMatrix()
    glTranslatef(-1.0, -0.25, 0.24)
    glRotatef(car_left_door_angle, 0, 1, 0)
    glTranslatef(0.5, 0.0, 0.0)
    glColor3f(1.0, 0.0, 0.0)
    glScalef(0.8, 0.5, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()


    # porta direita
    glPushMatrix()
    glTranslatef(1.0, -0.25, 0.24)
    glRotatef(-car_right_door_angle, 0, 1, 0)
    glTranslatef(-0.5, 0.0, 0.0)
    glColor3f(1.0, 0.0, 0.0)
    glScalef(0.8, 0.5, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()


    # wheels
    draw_wheel(-1.1, -0.5, 1.0, front_rotation, "left") # left front
    draw_wheel(1.1, -0.5, 1.0, front_rotation, "right") # right front
    draw_wheel(-1.1, -0.5, -1.0, back_rotation, "left", True) # left back
    draw_wheel(1.1, -0.5, -1.0, back_rotation, "right", True) # right back

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
    global door_opening, door_closing 
    global car_left_door_angle, car_right_door_angle
    global car_left_door_opening, car_left_door_closing
    global car_right_door_opening, car_right_door_closing

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
    elif key == b'o':  # Open door
        door_opening = True
        door_closing = False
    elif key == b'c':  # Close door
        door_closing = True
        door_opening = False
    elif key == b'r': #open right 
        car_right_door_closing = False
        car_right_door_opening = True
    elif key == b't': #close right 
        car_right_door_closing = True
        car_right_door_opening = False
    elif key == b'y': #open left
        car_left_door_closing = False
        car_left_door_opening = True
    elif key == b'u': # close left
        car_left_door_closing = True
        car_left_door_opening = False

    glutPostRedisplay() # redraw the scene

def display():
    global wheel_angle, cam_x, cam_z, car_angle, speed, car_x, car_z
    global garage_door_angle, door_opening, door_closing
    global car_left_door_angle, car_right_door_angle
    global car_left_door_opening, car_left_door_closing
    global car_right_door_opening, car_right_door_closing

    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if door_opening and garage_door_angle < 90:
        garage_door_angle += 3
        
    
    elif door_closing and garage_door_angle > 0:
        garage_door_angle -= 3

    
    speed *= friction
    if abs(speed) < 0.001:
        speed = 0

    car_angle += (speed * wheel_angle) / 50.0
    

    # update position
    car_x += speed * math.sin(math.radians(car_angle))
    car_z += speed * math.cos(math.radians(car_angle))


    #portas do carro
    door_step= 3.5

    # left door
    if car_left_door_opening and car_left_door_angle < 180.0:
        car_left_door_angle += door_step
        if car_left_door_angle > 180.0:
            car_left_door_angle = 180.0
            car_left_door_opening = False
    elif car_left_door_closing and car_left_door_angle > 90.0:
        car_left_door_angle -= door_step
        if car_left_door_angle < 90.0:
            car_left_door_angle = 90.0
            car_left_door_closing = False

    # right door
    if car_right_door_opening and car_right_door_angle < 180.0:
        car_right_door_angle += door_step
        if car_right_door_angle > 180.0:
            car_right_door_angle = 180.0
            car_right_door_opening = False
    elif car_right_door_closing and car_right_door_angle > 90.0:
        car_right_door_angle -= door_step
        if car_right_door_angle < 90.0:
            car_right_door_angle = 90.0
            car_right_door_closing = False


    # Câmara
    
    cam_dist = 10 #Distancia da camara ao carro

    # calcular nova posição da câmara
    cam_x = car_x - cam_dist * math.sin(math.radians(cam_angle))
    cam_z = car_z - cam_dist * math.cos(math.radians(cam_angle))

    cam_y = 6 #altura da camara

    # aplicar a nova camara
    gluLookAt(cam_x, cam_y, cam_z,
            car_x, car_y, car_z,
            0, 1, 0)


    draw_ground()  # draw the ground plane
    draw_garage_walls()   # Walls from garage.obj
    draw_garage_door()    # Animated door from door.obj
    draw_garage_switch()  # Light switch with indicator
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
