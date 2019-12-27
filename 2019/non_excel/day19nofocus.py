import time
import math

OUT_REPOSITION = "\x1b[0;0f"
OUT_CLEAR = "\x1b[3J]"

def abs(a):
    if a < 0:
        return -a
    return a

print(OUT_REPOSITION + OUT_CLEAR, end='')
while True:
    t = time.time()
    print(OUT_REPOSITION, end='')
    
    par_dir = math.sin(t)
    
    par_x = 80 - 70*par_dir
    par_y = 80 + 70*par_dir
    par_w = math.sin(t*1.73)*25 + 26
    
    count = 0
    for y in range(50):
        row = ""
        for x in range(50):
            if (par_w * y * x) >= abs(x*x*par_x - y*y*par_y):
                row += "##"
                count += 1
            else:
                row += ".."
        print(row)
    print("Count: %5d" % count)
