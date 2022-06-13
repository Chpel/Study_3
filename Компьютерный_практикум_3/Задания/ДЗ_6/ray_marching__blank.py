import time
import numpy as np
from shader_funcs import *

ti.init(arch=ti.gpu)
# ti.init(arch=ti.cpu)

#%% Resolution and pixel buffer

asp = 16/9
h = 600
w = int(asp * h)
res = w, h


#%% Fields (should always be before first call of any taichi scope kernels)

global_time = ti.field(dtype=ti.f32, shape=())
mouse_pos = ti.Vector.field(2, dtype=ti.f32, shape=())
mouse_btn = ti.field(dtype=ti.i32, shape=(2, ))
materials = ti.Vector.field(3, dtype=ti.f32, shape=(5,))
reflects = ti.field(dtype=ti.f32, shape=4)
pixels = ti.Vector.field(3, dtype=ti.f32, shape=res)

#%% Ray marching constants

MAX_STEPS = 200
MAX_DIST = 100.

AAMode = 2
step = 0.5 / AAMode
offset = np.linspace(-0.5 + step, 0.5 - step, AAMode)
offsetxy = np.meshgrid(offset, offset)
offsets = np.array([offsetxy[0].flatten(), offsetxy[1].flatten()]).T

ti_offsets = ti.Vector.field(n=2, dtype=ti.f32, shape=(AAMode ** 2))
ti_offsets.from_numpy(offsets)

TOON_SHADING=True

outline_width = -1.
if TOON_SHADING:
    outline_width = 0.03


inf = 1e10
eps = 1e-3
e_x = vec3(eps, 0., 0.)
e_y = vec3(0., eps, 0.)
e_z = vec3(0., 0., eps)

eye3 = mat3([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
#%% Materials

materials.from_numpy(np.array([
                               [ 76, 125,  18],   # green
                               [200,  50,  10],   # red
                               [ 94,  63,  43],   # brown
                               [ 0,   0,   0],  # black_outline
                               [128, 205, 230] # background
                              ],
                     dtype=np.float32) / 255.)


reflects.from_numpy(np.array([0.1,  # green
                              0.1,  # red
                              0.05,  # brown
                              0.0]  # background
                             ).astype(np.float32))

#%% Functions


@ti.func
def dist_vector(p):
    """distances to all scene objects"""
    t = global_time[None]

    p1 = p - vec3(-1., 0.7 + 0.15 * ti.sin(np.pi / 2 * t), 1)
    d1 = sd_sphere(p1, 0.5)
    d3 = p.y

    m = rot_y(np.pi/20.*t)
    p1 = m @ (p - vec3(2., 0.2, 2.))
    #d4 = sd_box(p1, vec3(0.5,0.5,0.5))
    d4 = sdPyramid(p1, 1.5)
    return vec3(d1, d4, d3)


@ti.func
def dist(p):
    """minimum distance to all objects in scene"""
    return dist_vector(p).min()


@ti.func
def dist_mat(p):
    """minimum distance to all objects in scene and material index of object closest to p"""
    return argmin(dist_vector(p))


@ti.func
def ray_march(ro, rd, ow):
    """
    функция поиска объекта на который "ложится" пиксель на экране:
    фигура, поверхность сцены (пол) или фон (небо)
    parameters:
        ro: вектор из которого мы наблюжаем за сценой и от которог отсчитываем лучи пикселей
        rd: вектор направления от "глаза" на пиксель экрана
    return:
        d: последнее опреденное расстояние от глаза до найденного объекта
        mat_i: индекс объекта
        p: вектор от глаза до найденного объекта
    """
    p = ro
    d = 0.
    ds, mat_i = dist_mat(p)
    min_dist = ds
    mat_i = 0
    for i in range(MAX_STEPS):
        min_dist = min(min_dist, ds)
        d += ds
        p = ro + d * rd
        ds, mat_i = dist_mat(p)
        if ds < eps:
            break
        if d > MAX_DIST:
            mat_i = -1
            break
        if ds > min_dist and min_dist < ow:
            mat_i = -2
            break
    return d, mat_i, p


@ti.func
def get_normal(p):
    """forward difference gradient calculation"""
    n = dist(p) - vec3(dist(p - e_x), dist(p - e_y), dist(p - e_z))
    return normalize(n)

@ti.func
def get_normal_d(p, d):
    """forward difference gradient calculation"""
    n = d - vec3(dist(p - e_x), dist(p - e_y), dist(p - e_z))
    return normalize(n)

@ti.func
def get_normal2(p, rd):
    n = dist(p) - vec3(dist(p - e_x), dist(p - e_y), dist(p - e_z))
    return normalize(n - max(0., dot(n, rd)) * rd)

@ti.func
def shadow(ro, rd):
    """
    базовая функция степени затенённости на объекте
    parameters:
        ro: вектор глаза
        rd: вектор направления луча на глаз
    returns:
        res: показатель затененности пикселя
    """
    d = 0
    t = eps * 10
    res = 1.
    for i in range(MAX_STEPS):
        h = dist(ro + rd * t)
        if h < eps:
            res = 0.
        t += h
    return res

@ti.func
def soft_shadow(ro, rd, k):  # ro: vec3, rd: vec3, mint: ti.f32, maxt: ti.f32, k: ti.f32
    """
    функция степени затенённости на объекте
    parameters:
        ro: вектор глаза
        rd: вектор направления луча на глаз
        k: базовая степень затененности
    returns:
        res: показатель затененности пикселя
    """
    # https://iquilezles.org/www/articles/rmshadows/rmshadows.htm
    t = eps * 10
    res = 1.
    for i in range(MAX_STEPS):
        h = dist(ro + rd * t)
        if h < eps:
            res = 0.
        res = min(res, k * h / t)
        t += h
    return res

@ti.func
def AmbientOcclusion(p, n):
    """
    функция внутреннего затененния на поверхности объектов
    parameters:
        p: вектор луча из глаза на пов-сть объекта
        n нормаль к пов-сти объекта
    returns:
        показатель внутренней затенённости пикселя
    """
    occ = 0.
    weight = 1.0
    for i in range(5):
        len = 0.01 + 0.02 * (i * i)
        d = dist(p + n * len)
        occ += (len - d) * weight
        weight *= 0.85
    return 1.0 - clamp(0.6 * occ, 0.0, 1.0)


@ti.func
def blinn_phong(n, rd, ld, sh):
    """
    :param n: normal to surface
    :param rd: ray direction
    :param ld: light direction
    :param sh: shininess
    :return:
    """
    vd = -rd  # view dir
    hd = normalize(ld + vd)  # half dir
    lamb = max(dot(ld, n), 0.0)
    spec = max(dot(hd, n), 0.0)**sh
    return lamb, spec

@ti.func
def render(ro, rd):  # ro: vec3, rd: vec3, t: ti.f32
    """
    основная функция определения цвета пикселя
    parameters:
        ro: вектор глаза
        rd: вектор направления луча на глаз
    returns:
        сol: цвет пикселя
        d: дальность от итогового луча от глаза
    """
    col = vec3(0.)
    d, mat_i, p = ray_march(ro, rd, outline_width)
    mat_n = materials.shape[0]
    background = materials[mat_n-1]
    t = global_time[None]
    mat_i = (mat_i + mat_n) % mat_n
    mate = materials[mat_i]


    if d < MAX_DIST:
        n = get_normal(p)
        #lp = vec3(3. * ti.sin(0.5 * t), 1.5, -3.)
        lp = vec3(5., 3.5, -5.)
        ld = normalize(lp - p)
        # ld = normalize(vec3(1., 1., -1.))
        lamb, spec = blinn_phong(n, rd, ld, 48)
        if mat_i == 1:
            m = rot_y(np.pi / 20. * t)
            p1 = m @ (p - vec3(2., 0.75, 2.))
            n1 = m @ (n)
            mate = triPlanar(p1, n1)

        if TOON_SHADING:
            lamb = ti.ceil(3. * lamb ** 0.5 ) / 3.
        if mat_i < mat_n-2:
            dif = mate * lamb
            amb = 0.3 * mate
            spe = vec3(1.) * spec
            occ = AmbientOcclusion(p, n)
            col += amb * occ + (dif + spe * occ) * soft_shadow(p, ld, 30)
        else:
            col += mate
    else:
        # background gradient
        col += background - max(0.9 * rd.y, 0.0)
    col = mix(col, background, smoothstep(20, 50, d))
    return col, d


@ti.kernel
def main_image():
    """
    процедура создания кадра на экране путем render'а каждого пикселя 
    (или субпикселей и их среднего цвета)
    """
    t = global_time[None]
    mp = ti.static(mouse_pos)
    mb = ti.static(mouse_btn)

    muv = 2 * np.pi * (mp[None] - 0.5)
    
    for fragCoord in ti.grouped(pixels):
        sumcol = vec3(0.,0.,0.)
        for i in ti.static(range(ti_offsets.shape[0])):
            uv = (fragCoord + ti_offsets[i] - 0.5 * vec2(res)) / res[1]

            ro = vec3(0., 1., -3.)
            a = 0.0 #t
            if mb[0] == 1:
                a += muv.x
                ro.z += muv.y
            m = rot_y(a)

            rd = normalize(vec3(uv.x, uv.y, 1.))

            ro = m @ ro
            rd = m @ rd
            col, d = render(ro, rd)

            # gamma correction
            col **= 1 / 2.2
            # col = ti.sqrt(col)
            sumcol += col
        pixels[fragCoord] = clamp(sumcol / ti_offsets.shape[0], 0., 1.)


#%% GUI and main loop

gui = ti.GUI("Taichi ray marching shader", res=res, fast_gui=True)
start = time.time()
video = True
once = True
stream = False
sec = 15
frames = 0

if video==True:
    OBS = ti.tools.VideoManager('./frames', width=res[0], height=res[1])

while gui.running and (frames <= 24 * sec):
    if gui.get_event(ti.GUI.PRESS):
        if gui.event.key == ti.GUI.ESCAPE:
            break
    mpos = gui.get_cursor_pos()  # [0..1], [0..1]
    mouse_pos[None] = [np.float32(mpos[0]), np.float32(mpos[1])]
    mouse_btn[0] = 1 if gui.is_pressed(ti.ui.LMB) else 0
    mouse_btn[1] = 1 if gui.is_pressed(ti.ui.RMB) else 0
    global_time[None] = frames / 12 #time.time() - start

    main_image()

    if once or stream:
        gui.set_image(pixels)
        gui.show()
        once = False

    if video:
        OBS.write_frame(pixels)

    print(frames)
    frames += 1

if video:
    OBS.make_video(mp4=True, gif=False)
gui.close()