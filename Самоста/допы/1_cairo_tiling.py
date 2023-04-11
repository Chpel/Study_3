pi = ti.math.pi

def Cairo(uv, k):
    id = floor(uv) #checkerboard
    check = (id.x + id.y) % 2 # 0 or 1
    #col += check
    
    uv = fract(uv)-0.5 #repeat pattern
    p = abs(uv)
    
    if (check==1.): #flip pattern
        p = p.yx
    
    a = (k*0.5+0.5)*pi
    n = vec2(sin(a), cos(a))
    
    if d*(check-0.5)>0.: #деление на области относительно пятиугольников, а не квадратов
        id.x += sign(uv.x)*0.5
    else:
        id.y += sign(uv.y)*0.5 
        
    
    d = dot(p-0.5 , n) #slanted line
    d = min(d, p.x)  #vertical connection
    d = max(d, -p.y) #horizontal connection
    d = min(d, dot(p-0.5, vec2(n.y, n.x))) #for all-pentagon cont-filling
    
    d = abs(d) # line forming
    
    return id, d
    
def res_filled():
    uv = (fragCoord - 0.5 * res) / res[1]
    muv = mouse.xy/res
    
    cos = vec3(0.)
    uv *= 4.1 #zoom down
    
    id, d = Cairo(uv, muv.y) #param2 for mouse orientation
    
    col += d #filing
    
    float r = hash21(id) #random id-wise blink
    col *= 1 + sin(r*2*pi+t)
    
    col += smoothstep(0.01, 0., d-0.01) #line forming
    
    #if ti.max(p.x, p.y) > 0.49: #box boundaries
    #    col[0] += 0.8
        
    return col