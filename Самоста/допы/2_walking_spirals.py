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

@ti.func
def mod1(p, size):
    """
    двойная функция остатков и округлений (ступеней)
    параметры:
        p: число для приведения
        size: ширина ступени или окна остатка
    returns:
        p: значение ступени
        c: значение остатка
    """
    halfsize = size*0.5
    c = ti.floor((p + halfsize)/size)
    p = (p + halfsize) % size - halfsize
    return p, c

@ti.func
def spiralLength(b, a):
    """
    функция длины дуги архимедовой спирали
    параметры:
        b: смещение радиуса за оборот
        a: угловая переменная, в радианах (мера оборотов спирали)
    """
    # https://en.wikipedia.org/wiki/Archimedean_spiral
    return 0.5*b*(a*ti.sqrt(1.0+a*a)+ti.log(a+ti.sqrt(1.0+a*a)))

@ti.func
def spiralMod(p: vec2, a):
    """
    параметры:
        p: вектор (хвоста или головы спирали)
        a: расстояние между смежными оборотами спирали
    возвращает:
        res: характеристики спирали в виде вектора (длина дуги, и число полных оборотов)
    """
    op = vec2(p)
    b = a / tau
    rr = length(op)
    aa = ti.math.atan2(op.y, op.x)
    rr -= aa*b
    rr, nn = mod1(rr, a)
    sa = aa + tau*nn
    sl = spiralLength(b, sa)
    res = vec2(sl, rr)
    return res

@ti.func
def segmentx(p: vec2, l, r):
    """
    параметры:
        p: вектор точки относительно центра спирали
        l: длина дуги спирали
        r: ширина спирали
    возвращает:
        res: расстояние до спирали
    """
    hl = l * 0.5 - r
    p.x = abs(p.x)
    d0 = abs(p.y) - r
    d1 = length(p - vec2(hl, 0.0)) - r
    res = d1 if p.x > hl else d0
    return res

@ti.func
def doubleSpiral(p: vec2, speed: float, toff: float, t: ti.f32):
    """
    функция генерации спирали: движущихся к центру головы и хвоста спирали
    
    параметры:
        p: вектор точки на плоскости
        speed: скорость движения спирали
        toff: случайная доля отклонения между головой и хвостом спирали 
        t: время для данного кадра
    возвращает:
        res: расстояние до спирали

    """
    tm = speed * t
    PERIOD = 14.0
    tm += PERIOD * (toff - 0.5)
    tm, _ = mod1(tm, PERIOD)
    a = fract(tm)
    nt = ti.floor(tm)
    lw = 0.01
    off = 0.376
    p.x -= nt * off + lw
    p.y *= mix(1.0, -1.0, nt % 2.0)
    sp0 = vec2(p)
    sp1 = vec2(p)

    sp1.x -= off
    sp1.y = -sp1.y

    sp0 = spiralMod(sp0, .05)
    sp1 = spiralMod(sp1, .05)

    sp2 = vec2(sp1)
    l = 8.87
    sp0.x -= 0.75 * l - a * l
    sp1.x -= 0.75 * l - (a - 1.0) * l

    d0 = segmentx(sp0, 0.5 * l, lw)
    d1 = segmentx(sp1, 0.5 * l, lw)
    d2 = -sp2.x + l

    d = d0
    d = ti.min(d, ti.max(-d2, d1))

    return d

@ti.func
def hash(co):

    return fract(ti.sin(co*12.9898) * 13758.5453)

@ti.func
def effect(p: vec2, pp: vec2, t: ti.f32):
    """
    основная функция определения цвета пикселя
    параметры:
        p: приведённый вектор (с наложенным поворотом и масштабированием относительно сторон экрана)
        pp: истинный вектор пикселя (экран - множество пар чисел в промежутке [-1,1]^2)
    возвращает:
        сol: цвет пикселя
    """
    aa = 2.0/res[1]
    col = vec3(0.)

    for i in range(7.):
        sp = vec2(p)
        sp = sp @ rot(tau*i/3.5)
        sp.y, nx = mod1(sp.y, 1.0)
        h0 = hash(nx+123.2+i)
        h1 = fract(3677.0*h0)
        h2 = fract(8677.0*h0)
        h3 = fract(9677.0*h0)
        z = mix(0.66, 1.0, h2)
        sp /= z
        dd = doubleSpiral(sp, 0.5*mix(0.1, 0.4, h0*h0), h1, t)*z
        bcol = (1.0+ti.cos(1.5*vec3(2.0, 0.0, -1.0)+tau*h3))
        col += bcol*smoothstep(aa, -aa, dd)

    col = 1.0-ti.tanh(col.yxz)
    col *= vec3(1.0, 0.95, 0.95)
    col = ti.sqrt(col)
    return col

# %% Kernel
@ti.kernel
def render(t: ti.f32, frame: ti.int32):
    """
    процедура создания кадра на экране путем render'а каждого пикселя 
    параметры:
        t: время от начала выполнения программы
        frame: номер выполняемого кадра (более подходящая хар-ка времени при записи видео)
    """
    for fragCoord in ti.grouped(pixels):
        q = fragCoord / res
        p = -1. + 2. * q
        pp = vec2(p)
        p.x *= res[0]/res[1]
        #p = ROT(-0.1*t) * (p);
        #p = (p - 0.1 * t * sin(hash22(vec2(1.))));
        col = effect(p, pp, t)

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


"""
// CC0: Walking spirals
//  Once again inspired by twitter stuff: https://twitter.com/junkiyoshi/status/1632340637218672641?s=20

#define TIME        iTime
#define RESOLUTION  iResolution
#define PI          3.141592654
#define TAU         (2.0*PI)
#define ROT(a)      mat2(cos(a), sin(a), -sin(a), cos(a))

// License: MIT OR CC-BY-NC-4.0, author: mercury, found: https://mercury.sexy/hg_sdf/
float mod1(inout float p, float size) {
  float halfsize = size*0.5;
  float c = floor((p + halfsize)/size);
  p = mod(p + halfsize, size) - halfsize;
  return c;
}

float spiralLength(float b, float a) {
  // https://en.wikipedia.org/wiki/Archimedean_spiral
  return 0.5*b*(a*sqrt(1.0+a*a)+log(a+sqrt(1.0+a*a)));
}

void spiralMod(inout vec2 p, float a) {
  vec2 op     = p;
  float b     = a/TAU;
  float  rr   = length(op);
  float  aa   = atan(op.y, op.x);
  rr         -= aa*b;
  float nn    = mod1(rr, a);
  float sa    = aa + TAU*nn;
  float sl    = spiralLength(b, sa);
  p           = vec2(sl, rr);
}

float segmentx(vec2 p, float l, float r) {
  float hl = l*0.5-r;
  
  p.x = abs(p.x);
  
  float d0 = abs(p.y) -r;
  float d1 = length(p - vec2(hl, 0.0))-r;
  return p.x > hl ? d1 : d0;
}

vec3 doubleSpiral(vec2 p, float speed, float toff) {
  float tm = speed*TIME;
  const float PERIOD = 14.0;
  tm += PERIOD*(toff-0.5);
  mod1(tm, PERIOD);
  float a = fract(tm);
  float nt = floor(tm);

  const float lw = 0.01;
  const float off = 0.376;
  p.x -= (nt)*off+lw;
  p.y *= mix(1.0, -1.0, mod(nt, 2.0));
  vec2 sp0 = p;
  vec2 sp1 = p;
  
  sp1.x -= off;
  sp1.y = -sp1.y;
  
  spiralMod(sp0, .05);
  spiralMod(sp1, .05);

  vec2 sp2 = sp1;

  const float l = 8.87;
  sp0.x -= 0.75*l - a*l;
  sp1.x -= 0.75*l - (a-1.0)*l;

  float d0 = segmentx(sp0, 0.5*l, lw);
  float d1 = segmentx(sp1, 0.5*l, lw);
  float d2 = -sp2.x+l;
  
  float dres = min(d0, max(-d2, d1));
  float id = 0.;
  if (dres == d0) {
      id = 0.;
  }
  else if (dres == -d2) {
      id = 2.;
  }
  else id = 1.;
  
  return vec3(dres, id, float(mod(nt, 2.)));
}

// License: Unknown, author: Unknown, found: don't remember
float hash(float co) {
  return fract(sin(co*12.9898) * 13758.5453);
}

vec2 hash22(vec2 co) {
  return fract(sin(co*12.9898) * 13758.5453);
}


vec3 effect(vec2 p, vec2 pp) {
  float aa = 2.0/RESOLUTION.y;
  vec3 col = vec3(0.0);

  for (float i = 0.0; i < 7.0; ++i) {
    vec2 sp = p;
    sp *= ROT(TAU*i/3.5);
    float nx = mod1(sp.y, 1.0);
    float h0 = hash(nx+123.2+i);
    float h1 = fract(3677.0*h0);
    float h2 = fract(8677.0*h0);
    float h3 = fract(9677.0*h0);
    float z = mix(0.66, 1.0, h2); 
    sp /= z;
    vec3 dvec = doubleSpiral(sp, 0.5*mix(0.1, 0.4, h0*h0), h1);
    float dd = dvec.x * z;
    float id = dvec.y;
    float per_id = dvec.z;
    vec3 acol = (1.0+cos(1.5*vec3(2.0, 0.0, -1.0)+TAU*h1));
    vec3 bcol = (1.0+cos(1.5*vec3(2.0, 0.0, -1.0)+TAU*h2));
    if (id == 0.) col += (per_id * bcol + float(mod(per_id + 1., 2.)) * acol) * smoothstep(aa, -aa, dd);
    if (id == 1.) col += (per_id * acol + float(mod(per_id + 1., 2.)) * bcol) * smoothstep(aa, -aa, dd);
  }

  col = 1.0-tanh(col.yxz);
  col *= vec3(1.0, 0.95, 0.95);
  col = sqrt(col);
  return col;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
  float t = TIME;
  vec2 q = fragCoord/RESOLUTION.xy;;
  vec2 p = -1. + 2. * q;
  vec2 pp = p;
  p.x *= RESOLUTION.x/RESOLUTION.y;
  p = ROT(-0.1*t) * (p);
  p = (p - 0.1 * t * sin(hash22(vec2(1.))));

  vec3 col = effect(p, pp);
  
  fragColor = vec4(col, 1.0);
}
"""