import taichi as ti
from shader_funcs import *
import time

ti.init(arch=ti.gpu)

# %% Resolution and pixel buffer

asp = 16 / 9
h = 600
w = int(asp * h)
res = w, h
tau = 2. * ti.math.pi
pixels = ti.Vector.field(3, dtype=ti.f32, shape=res)
vres = vec2(res) * 1.

pi = ti.math.pi

@ti.func
def Cairo(uv, k):
    """
    основная функция определения цвета пикселя в стиле каирской плитки
    параметры:
        uv: вектор пикселя на экране
        k: параметр структурного отклонения рёбер пятиугольников
    возвращает:
        id: код пятиугольника, на котором лежит плитка
        d: расстояние до ближайшего ребра
    """
    id = ti.floor(uv)  # checkerboard
    check = (id.x + id.y) % 2 # 0 or 1
    #    col += check

    uv = fract(uv) - 0.5  # repeat pattern
    p = ti.abs(uv)

    if (check == 1):  # flip pattern
        p = p.yx

    a = (k * 0.5 + 0.5) * pi
    n = vec2(ti.sin(a), ti.cos(a))
    d = dot(p - 0.5, n)  # slanted line

    if d * (check - 0.5) < 0.:  # деление на области относительно пятиугольников, а не квадратов
        id.x += sign(uv.x) * 0.5
    else:
        id.y += sign(uv.y) * 0.5

    d = ti.min(d, p.x)  # vertical connection
    d = ti.max(d, -p.y)  # horizontal connection
    d = abs(d)  # line forming
    d = ti.min(d, dot(p - 0.5, vec2(n.y, - n.x)))  # for all-pentagon cont-filling
    return id, d
    



@ti.kernel
def render(t: ti.f32, frame: ti.int32):
    """
    процедура создания кадра на экране путем render'а каждого пикселя 
    параметры:
        t: время от начала выполнения программы
        frame: номер выполняемого кадра (более подходящая хар-ка времени при записи видео)
    """
    for fragCoord in ti.grouped(pixels):
        uv = (fragCoord - vres * 0.5) / vres.y
        muv = vec2(0, 0.4)#(ti.sin(0.4 * t) + 1.) * 0.5)

        col = vec3(0.)
        uv *= 3.1  # zoom down

        id, d = Cairo(uv, muv.y)  # param2 for mouse orientation
        col += d

        r = hash21(id)  # random id-wise blink
        col *= 1 + ti.sin(r * 2 * pi + t)

        col += smoothstep(0.01, 0., d - 0.005)  # line forming
        pixels[fragCoord] = col

    # %% GUI and main loop


gui = ti.GUI("Taichi simple shader", res=res, fast_gui=True)
frame = 0
start = time.time()

while gui.running:
    if gui.get_event(ti.GUI.PRESS):
        if gui.event.key == ti.GUI.ESCAPE:
            break

    t = time.time() - start
    render(t, frame)
    gui.set_image(pixels)
    gui.show()
    frame += 1

gui.close()