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
    halfsize = size*0.5
    c = ti.floor((p + halfsize)/size)
    p = (p + halfsize) % size - halfsize
    return p, c

@ti.func
def spiralLength(b, a):
# https://en.wikipedia.org/wiki/Archimedean_spiral
    return 0.5*b*(a*ti.sqrt(1.0+a*a)+ti.log(a+ti.sqrt(1.0+a*a)))

@ti.func
def spiralMod(p: vec2, a):
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
    hl = l * 0.5 - r
    p.x = abs(p.x)
    d0 = abs(p.y) - r
    d1 = length(p - vec2(hl, 0.0)) - r
    res = d1 if p.x > hl else d0
    return res

@ti.func
def doubleSpiral(p: vec2, speed: float, toff: float, t: ti.f32):
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
    col00 = vec3(0.50, 0.50, 0.50)
    col01 = vec3(1.00, 1.00, 1.00)
    col02 = vec3(0.00, 0.03, 0.67)
    col03 = vec3(0.00, 0.10, 0.20)

    for fragCoord in ti.grouped(pixels):
        q = fragCoord / res
        p = -1. + 2. * q
        pp = vec2(p)
        p.x *= res[0]/res[1]
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