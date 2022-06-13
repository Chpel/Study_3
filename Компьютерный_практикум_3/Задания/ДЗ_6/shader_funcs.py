import taichi as ti
import math

# %% type shortcuts

vec2 = ti.types.vector(2, ti.f32)
vec3 = ti.types.vector(3, ti.f32)
vec4 = ti.types.vector(4, ti.f32)
vec5 = ti.types.vector(5, ti.f32)
vec6 = ti.types.vector(6, ti.f32)
vec7 = ti.types.vector(7, ti.f32)
vec8 = ti.types.vector(8, ti.f32)
vec9 = ti.types.vector(9, ti.f32)
vec10 = ti.types.vector(10, ti.f32)
vec11 = ti.types.vector(11, ti.f32)
vec12 = ti.types.vector(12, ti.f32)
vec13 = ti.types.vector(13, ti.f32)
vec14 = ti.types.vector(14, ti.f32)
vec15 = ti.types.vector(15, ti.f32)
vec16 = ti.types.vector(16, ti.f32)

mat2 = ti.types.matrix(2, 2, ti.f32)
mat3 = ti.types.matrix(3, 3, ti.f32)
mat4 = ti.types.matrix(4, 4, ti.f32)


tmpl = ti.template()
# %% constants

twopi = 2 * math.pi
pi180 = math.pi / 180.

# %% shader language functions


@ti.func
def length(p):
    """
    возвращает модуль вектора
    parameters
        p: вектор
    returns
        модуль вектора
    """
    return ti.sqrt(p.dot(p))


@ti.func
def normalize(p):
    """
    возвращает нормированный вектор длины 1
    parameters
        p: вектор
    returns
        нормированный вектор длины 1
    """
    n = p.norm()
    return p / (n if n != 0. else 1.)


@ti.func
def mix(x, y, a):
    """
    возвращает объект между x и y
    parameters
        x, y: вектора (в программе чаще всего обозначают цвета)
        a: параметр смешения векторов
    returns
        вектор между x и y (или цвет полученный смешением x и y в пропорции a)
    """
    return x * (1. - a) + y * a


@ti.func
def dot(p, q):
    """
    скалярное произведение
    parameters
        p, q: вектор
    returns
        скалярное произведение p и q
    """
    return p.dot(q)


@ti.func
def dot2(p):
    """
    собственное скалярное произведение
    parameters
        p: вектор
    returns
        скалярное произведение p и p
    """
    return p.dot(p)


@ti.func
def cross(x, y):
    """
    векторное произведение
    parameters
        x,y: вектора длины 3
    returns
        векторное произведение <x,y>
    """
    # {x[1] \times y[2] - y[1] \times x[2]}
    # {x[2] \times y[0] - y[2] \times x[0]}
    # {x[0] \times y[1] - y[0] \times x[1]}
    return vec3(x[1] * y[2] - y[1] * x[2],
                x[2] * y[0] - y[2] * x[0],
                x[0] * y[1] - y[0] * x[1])


@ti.func
def reflect(rd, n):  # rd: vec3, n: vec3
    # https: // www.khronos.org / registry / OpenGL - Refpages / gl4 / html / reflect.xhtml
    """reflect incident vector rd using surface normal n"""
    return rd - 2.0 * dot(n, rd) * n


@ti.func
def deg2rad(a):
    """
    перевод градусов в радианы
    parameters:
        a: градусы
    returns:
        значение радианов
    """
    return a * pi180


@ti.func
def rot(a):
    """
    матрица поворота на плоскости
    parameters:
        a: угол в радианах
    returns:
        матрица поворота на плоскости на А радиан
    """
    c = ti.cos(a)
    s = ti.sin(a)
    return mat2([[c, -s], [s, c]])


@ti.func
def rot_y(a):
    """
    матрица поворота в 3D пространстве вокруг оси oY
    parameters:
        a: угол в радианах
    returns:
        матрица поворота в 3D пространстве вокруг оси oY на А радиан
    """
    c = ti.cos(a)
    s = ti.sin(a)
    return mat3([[c, 0, -s],
                 [0, 1,  0],
                 [s, 0,  c]])


@ti.func
def rot_x(a):
    """
    матрица поворота в 3D пространстве вокруг оси oX
    parameters:
        a: угол в радианах
    returns:
        матрица поворота в 3D пространстве вокруг оси oX на А радиан
    """
    c = ti.cos(a)
    s = ti.sin(a)
    return mat3([[1, 0,  0],
                 [0, c, -s],
                 [0, s,  c]])


@ti.func
def rot_z(a):
    """
    матрица поворота в 3D пространстве вокруг оси oZ
    parameters:
        a: угол в радианах
    returns:
        матрица поворота в 3D пространстве вокруг оси oZ на А радиан
    """
    c = ti.cos(a)
    s = ti.sin(a)
    return mat3([[c, -s, 0],
                 [s,  c, 0],
                 [0,  0, 1]])

@ti.func
def sign(x: ti.f32):
    """
    функция знака числа
    parameters:
        x: число
    returns:
        знак числа: +-1 или 0
    """
    return 1. if x > 0. else -1. if x < 0. else 0.


@ti.func
def signv(x: tmpl):
    """
    функция знака вектора
    parameters:
        x: вектор
    returns:
        вектор со значениями знака каждого числа в x: +-1 или 0
    """
    r = ti.Vector(x.shape[0], x.dtype)
    for i in ti.static(range(x.shape[0])):
        r[i] = sign(x[i])
    return r


@ti.func
def clamp(x, low, high):
    """
    функция ограничения сверху и снизу
    parameters:
        x: число
        low: нижняя граница
        high: верхняя граница
    returns:
        x если оно в области [low, high], иначе его ограничитель 
    """
    return ti.max(ti.min(x, high), low)


@ti.func
def fract(x):
    """
    функция дробной части
    parameters:
        x: число или вектор
    returns:
        число или вектор, содержащий только дробную часть вводимого параметра
    """
    return x - ti.floor(x)


@ti.func
def step(edge, x):
    """
    органичение справа
    parameters:
        edge: край
        x: число
    returns:
        логич. переменная перехода за край
    """
    return 0. if x < edge else 1.


@ti.func
def smoothstep(edge0, edge1, x):
    """
    функция гладкого нелинейного шага
    parameters:
        edge0,edge1: края плавного шага
        x: число
    returns:
        значение плавного шага
    """
    n = (x - edge0) / (edge1 - edge0)
    t = clamp(n, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


@ti.func
def smoothmin(a, b, k):
    """
    функция гладкого минимума
    parameters:
        a, b: числа
        k: параметр сглаживания
    returns:
        значение функции гладкого минимума
    """
    h = max(k - abs(a - b), 0.) / k
    return min(a, b) - h * h * k * (1./4.)


@ti.func
def smoothmax(a, b, k):
    """
    функция гладкого максимума
    parameters:
        a, b: числа
        k: параметр сглаживания
    returns:
        значение функции гладкого максимума
    """
    return smoothmin(a, b, -k)


@ti.func
def smoothmin3(a, b, k):
    """
    функция гладкого минимума в 3D пространстве
    parameters:
        a, b: числа
        k: параметр сглаживания
    returns:
        значение функции гладкого минимума
    """
    h = max(k - abs(a - b), 0.) / k
    return min(a, b) - h * h * h * k * (1./6.)


@ti.func
def skewsin(x, t):
    """
    функция пологого синуса
    parameters:
        x, t: параметры
    returns:
        вектор из двух значений - {пологий синус, пологий косинус}
    """
    return ti.atan2(t * ti.sin(x), (1. - t * ti.cos(x))) / t

#%% PRNG

@ti.func
def random2():
    """
    функция случайного 2D-вектора
    parameters:
    
    returns:
        случайный 2D-вектор
    """
    return vec2(ti.random(ti.f32), ti.random(ti.f32))


"""
Семество функций псевдослучайных чисел HASH с вводимым начальным состоянием по принципу резкого увеличения числа
и полученния дробной части в качестве результата - дешёвый генератор действительных чисел [0,1]
parameters:
    n или p: начальное состояние по которому рассчитывается случайные число или вектор
returns:
    случайные число или вектор
"""

@ti.func
def hash1(n):
    return fract(ti.sin(n) * 43758.5453)


@ti.func
def hash21(p):
    q = fract(p * vec2(123.34, 345.56))
    q += dot(q, q + 34.23)
    return fract(q.x * q.y)

@ti.func
def hash31(p):
    q = fract(p * vec3(123.34, 345.56, 567.78))
    q += dot(q, q + 34.23)
    return fract(q.x * q.y * q.z)


@ti.func
def hash22(p):
    x = hash21(p)
    y = hash21(p + x)
    return vec2(x, y)


@ti.func
def hash33(p):
    x = hash31(p)
    y = hash31(p + x)
    z = hash31(p + x + y)
    return vec3(x, y, z)


# https://www.shadertoy.com/view/ll2GD3
@ti.func
def pal(t, a, b, c, d):
    """
    непрерывная функция задания цвета между 4-мя заданными цветами
    parameters:
        t: время
        a,b,c,d: vec3-цвета
    returns:
        цвет между 4-мя заданными цветами
    """
    return a + b * ti.cos(twopi * (c * t + d))

#%% SDF 2D

@ti.func
def sd_circle(p, r):  # == sd_sphere
    """
    SDF-Функция для определения расстояния до круга или сферы
    parameters:
        p: рассматриваемый вектор сцены
        r: радиус круга/сферы
    returns:
        расстояние до поверхности круга/сферы (если < 0, то внутри)
    """
    return p.norm() - r


@ti.func
def sd_segment(p, a, b):  # same for 3D
    """
    SDF-Функция для определения расстояния до сегмента
    parameters:
        p: рассматриваемый вектор сцены
        a,b: точки концов сегмента
    returns:
        расстояние до сегмента (если < 0, то внутри)
    """
    pa = p - a
    ba = b - a
    h = clamp(dot(pa, ba) / dot2(ba), 0.0, 1.0)
    return (pa - ba * h).norm()


@ti.func
def sd_box(p, b):  # same for 3D
    """
    SDF-Функция для определения расстояния до прям. параллелепипеда
    parameters:
        p: рассматриваемый вектор сцены
        b: стороны коробки в виде vec3
    returns:
        расстояние до прям. параллелепипеда (если < 0, то внутри)
    """
    d = abs(p) - b
    return max(d, 0.).norm() + min(d.max(), 0.0)


@ti.func
def sd_roundbox(p, b, r):
    """
    SDF-Функция для определения расстояния до круглоугольного параллелепипеда
    parameters:
        p: рассматриваемый вектор сцены
        b: стороны коробки в виде vec3
        r: радиус загругления
    returns:
        расстояние до круглоугольного параллелепипеда (если < 0, то внутри)
    """
    rr = vec2(r[0], r[1]) if p[0] > 0. else vec2(r[2], r[3])
    rr[0] = rr[0] if p.y > 0. else rr[1]
    q = abs(p) - b + rr[0]
    return min(max(q[0], q[1]), 0.) + max(q, 0.0).norm() - rr[0]


#%% SDF 3D
# https://www.iquilezles.org/www/articles/distfunctions/distfunctions.htm


@ti.func
def length2(p):
    """
    функция модуля 2-й степени 
    parameters:
        p: vector
    returns:
        модуля 2-й степени вектора p
    """
    return length(p)


@ti.func
def length6(p):
    """
    функция модуля 6-й степени 
    parameters:
        p: vector
    returns:
        модуля 6-й степени вектора p
    """
    q = p * p * p
    q *= q
    return (q.x + q.y + q.z)**(1./6.)


@ti.func
def length8(p):
    """
    функция модуля 8-й степени 
    parameters:
        p: vector
    returns:
        модуля 8-й степени вектора p
    """
    q = p * p
    q *= q
    q *= q
    return (q.x + q.y + q.z)**(1./8.)


@ti.func
def ndot(a, b):
    """
    скалярное произведение
    parameters:
        a,b: 2D-вектора 
    returns:
        (a,b)
    """
    return a.x*b.x - a.y*b.y


@ti.func
def sd_sphere(p, r):
    """
    SDF-Функция для определения расстояния до круга или сферы
    parameters:
        p: рассматриваемый вектор сцены
        r: радиус круга/сферы
    returns:
        расстояние до поверхности круга/сферы (если < 0, то внутри)
    """
    # same as sd_circle
    return length(p) - r


@ti.func
def sd_torus(p, r):  # p: vec3, t: vec2
    """
    SDF-Функция для определения расстояния до тора
    parameters:
        p: рассматриваемый вектор сцены
        r: радиусы тора (внутренний и внешний)
    returns:
        расстояние до поверхности круга/сферы (если < 0, то внутри)
    """
    q = vec2(length(vec2(p.x, p.z)) - r.x, p.y)
    return length(q) - r.y


@ti.func
def sd_cylinder(p, c):  # p: vec3, c: vec3
    """
    SDF-Функция для определения расстояния до бесконечно длинного цилиндра
    parameters:
        p: рассматриваемый вектор сцены
        с: центр и радиус цилиндра
    returns:
        расстояние до поверхности бесконечно длинного цилиндра (если < 0, то внутри)
    """
    pxz = vec2(p.x, p.z)
    cxy = vec2(c.x, c.y)
    return length(pxz - cxy) - c.z


@ti.func
def sd_cappedcylinder(p, h, r):  # p: vec3, h: ti.f32, r: ti.f32
    """
    SDF-Функция для определения расстояния до ограниченного цилиндра
    parameters:
        p: рассматриваемый вектор сцены
        h: высота цилиндра
        r: радиус цилиндра
    returns:
        расстояние до поверхности цилиндра (если < 0, то внутри)
    """
    pxz = vec2(p.x, p.z)
    d = abs(vec2(length(pxz), p.y)) - vec2(h, r)
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0))


@ti.func
def sd_cone(p, c, h):  # p: vec3, c: vec2, h: ti.f32
    """
    c is the sin / cos of the angle, h is height
    Alternatively pass q instead of(c, h), which is the
    point at the base in 2D
    """
    q = h * vec2(c.x / c.y, -1.0)
    w = vec2(length(p.xz), p.y)
    a = w - q * clamp(dot(w, q) / dot(q, q), 0.0, 1.0)
    b = w - q * vec2(clamp(w.x / q.x, 0.0, 1.0), 1.0)
    k = sign(q.y)
    d = min(dot(a, a), dot(b, b))
    s = max(k * (w.x * q.y - w.y * q.x), k * (w.y - q.y))
    return ti.sqrt(d) * sign(s)


@ti.func
def sd_ellipsoid(p, r):  # p: vec3, r: vec3
    """
    SDF-Функция для определения расстояния до эллипсоида
    parameters:
        p: рассматриваемый вектор сцены
        r: радиусы эллипсоида
    returns:
        расстояние до поверхности эллипсоида (если < 0, то внутри)
    """
    pr = p / r
    k0 = length(pr)
    k1 = length(pr/r)
    return k0 * (k0 - 1.0) / k1


@ti.func
def op_rep(p, c):  # p: vec3, c: vec3
    """
    функция имитации бесконечного повторения объекта через некоторый интервал
    parameters:
        p: вектор сцены:
        с: периоды по каждой координате
    returns:
        вектор повторяющегося подпространства, который можно использовать в примитивах
    """
    c_half = 0.5 * c
    return (p + c_half) % c - c_half


@ti.func
def op_replim(p, c, l):  # p: vec3, c: ti.f32, l: vec3
    """
    функция имитации конечного повторения объекта через некоторый интервал
    parameters:
        p: вектор сцены
        с: периоды по каждой координате
        l: границы подпространства
    returns:
        вектор ограниченно повторяющегося подпространства, который можно использовать в примитивах
    """
    return p - c * clamp(ti.round(p / c), -l, l)


@ti.func
def op_cheapbend(p, k):  # p: vec3, k: ti.f32
    """
    функция имитации искажения объекта
    parameters:
        p: вектор сцены
        k: коэф. искривления
    returns:
        вектор искривленного пространства, который можно использовать в примитивах
    """
    alpha = k * p.x
    m = rot(alpha)
    q = m @ p.xy
    return vec3(q.x, q.y, p.z)

#%%

@ti.func
def lookat_raydir(uv, p, l, z):  # uv: vec2, p: vec3, l: vec3, z: ti.f32
    """
    :param uv: pixel coordinates
    :param p: camera position?
    :param l: camera look_at?
    :param z: scale?
    :return:
    """
    f = normalize(l - p)
    r = normalize(cross(vec3(0., 1., 0.), f))
    u = cross(f, r)
    c = f * z
    i = c + uv.x * r + uv.y * u
    return normalize(i)


@ti.func
def argmin(v):
    """
    функция поиска индекса мин. элемента
    parameters:
        v: массив
    returns:
        m: мин. значение
        j: его индекс в массиве
    """
    m = v[0]
    j = 0
    for i in ti.static(range(1, len(v))):
        if v[i] < m:
            j = i
            m = v[i]
    return m, j


#новые примитивы

@ti.func
def sdPyramid(p, h):
    """
    SDF-Функция для определения расстояния до пирамиды
    parameters:
        p: рассматриваемый вектор сцены
        h - высота пирамиды
    returns:
        расстояние до поверхности пирамиды
    """
    m2 = h*h + 0.25

    pxz = abs(vec2(p.x, p.z))
    if (pxz[1] > pxz[0]):
        temp = pxz[0]
        pxz[0] = pxz[1]
        pxz[1] = temp
    pxz -= 0.5
    p.x = pxz[0]
    p.z = pxz[1]

    q = vec3(p.z, h*p.y - 0.5*p.x, h*p.x + 0.5*p.y)

    s = max(-q.x,0.0)
    t = clamp((q.y-0.5*p.z)/(m2+0.25), 0.0, 1.0)

    a = m2*(q.x+s)*(q.x+s) + q.y*q.y
    b = m2*(q.x+0.5*t)*(q.x+0.5*t) + (q.y-m2*t)*(q.y-m2*t)
    d2 = 0.
    if min(q.y,-q.x*m2-q.y*0.5) > 0.0:
        d2 = 0.
    else:
        d2 = min(a,b)

    return ti.sqrt( (d2+q.z*q.z)/m2 ) * sign(max(q.z,-p.y))

@ti.func
def sdOctahedron(p, s):
    """
    SDF-Функция для определения расстояния до Октаэдрона
    parameters:
        p: рассматриваемый вектор сцены
        h - сторона октаэдрона
    returns:
        расстояние до поверхности октаэдрона
    """
    p = abs(p)
    return (p.x+p.y+p.z-s)*0.57735027

@ti.func
def sdDeathStar(p2, ra, rb, d):
    """
    SDF-Функция для определения расстояния до Звезды Смерти))
    parameters:
        p: рассматриваемый вектор сцены
        ra: радиус шара
        rb: радиус шара-пустоты
        b расстояние между центрами шара и его пустоты
    returns:
        расстояние до поверхности ЗС
    """
    #sampling independent computations (only depend on shape)
    a = (ra*ra - rb*rb + d*d)/(2.0*d)
    b = ti.sqrt(max(ra*ra-a*a,0.0))

    #sampling dependant computations
    p = vec2( p2.x, length(vec2(p2.y,p2.z)))
    d = 1
    if(p.x*b-p.y*a > d*max(b-p.y,0.0)):
        d = length(p-vec2(a,b))
    else:
        d = max( (length(p)-ra),-(length(p-vec2(d,0))-rb))
    return d

@ti.func
def sdRoundCone(p, r1, r2, h):
    """
    SDF-Функция для определения расстояния до закругленного конуса
    parameters:
        p: рассматриваемый вектор сцены
        r1, r2 - радиусы концов конуса
        h - расстояние между центрами шаров-концов
    returns:
        расстояние до поверхности конуса
    """
    # sampling independent computations (only depend on shape)
    b = (r1-r2)/h
    a = ti.sqrt(1.0-b*b)

    # sampling dependant computations
    q = vec2( length(vec2(p.x, p.z)),p.y)
    k = dot(q,vec2(-b,a))
    d = None
    if(k<0.0):
        d = length(q) - r1
    elif(k>a*h):
        d = length(q-vec2(0.0,h)) - r2
    else:
        d = dot(q, vec2(a,b) ) - r1
    return d


@ti.func
def sdRhombus(p, la, lb, h, ra):
    """
    SDF-Функция для определения расстояния до плоского ромба
    parameters:
        p: рассматриваемый вектор сцены
        la, lb: высоты ромба
        h: толщина ромба
        ra: радиус закругления углов
    returns:
        расстояние до поверхности октаэдрона
    """
    p = abs(p)
    b = vec2(la,lb)
    f = clamp( (ndot(b,b-2.0*vec2(p.x, p.z)))/dot(b,b), -1.0, 1.0 )
    q = vec2(length(vec2(p.x, p.z)-0.5*b*vec2(1.0-f,1.0+f))*sign(p.x*b.y+p.z*b.x-b.x*b.y)-ra, p.y-h)
    return min(max(q.x,q.y),0.0) + length(max(q,0.0))


@ti.func
def texture_box(uv):
    """
    Функция задачи цвета на поверхности фигуры (кубическая версия)
    parameters:
        uv: 2D-"координата" на поверхности фигуры
    returns:
        col: итоговый цвет пикселя
    """
    col00 = vec3(0.50, 0.50, 0.50)
    col01 = vec3(1.00, 1.00, 1.00)
    col02 = vec3(0.00, 0.33, 0.67)
    col03 = vec3(0.00, 0.10, 0.20)
    uv = 3. * (uv)
    fuv = fract(uv) - 0.5
    id = ti.floor(uv)
    d = 100000.
    circ = sd_sphere(fuv, 0.1 + 0.1 * hash22(id).x)
    d = smoothmin(d, circ, 0.4)
    col_x = mix(col02, col03, 1.)
    col = pal(d * ti.cos(uv.x + uv.y), col00, col00, col01, col_x)
    if d < 0.:
        col *= 0.8 + 0.2 * skewsin(64. * d, 0.7)
    else:
        col *= 0.9 + 0.1 * ti.cos(16. * d)
    col *= 1. - ti.exp(-20. * abs(d))
    return col

@ti.func
def triPlanar(p, normal):
    """
    Функция перевода вектора, попавшего на поверхность фигуры в 2D вектор
    parameters:
        p: рассматриваемый вектор сцены
        normal: нормаль к поверхности фигуры на которую попал вектор
    returns:
        цвет пикселя, вектор которого попал на фигуру
    """
    normal = abs(normal)
    normal = pow(normal, vec3(5.0))
    normal /= normal.x + normal.y + normal.z
    return texture_box(vec2(p.x, p.y) * 0.5 + 0.5) * normal.z + \
            texture_box(vec2(p.x, p.z) * 0.5 + 0.5) * normal.y + \
            texture_box(vec2(p.y, p.z) * 0.5 + 0.5) * normal.x