from math import *

""" Tuneables """
# extrusion parameters (mm)
extrusion_width = 0.4
layer_height = 0.2
filament_diameter = 1.75
hotend_temp = 205
bed_temp = 60

# print speeds (mm/s)
travel_speed = 150
first_layer_speed = 20
slow_speed = 5
fast_speed = 70

# calibration object dimensions (mm)
layers = 100
object_width = 100
num_patterns = 4
pattern_width = 5

# pressure advance gradient (s)
pressure_advance_min = 0.000
pressure_advance_max = 1.000

# center of print bed (mm)
offset_x = 150
offset_y = 150

# alerting
alerting = 'no'
#alerting = 'yes'

# Load mesh, valid values are: Duet, Marlin or None
mesh_type = None
# mesh_type = 'Marlin'
# mesh_type = 'Duet'

""" end tuneables """

def extrusion_volume_to_length(volume):
    return volume / (filament_diameter * filament_diameter * 3.14159 * 0.25)

def extrusion_for_length(length):
    return extrusion_volume_to_length(length * extrusion_width * layer_height)
layer0_z = layer_height
curr_x = offset_x
curr_y = offset_y
curr_z = layer0_z

# setting the temp
print(f"""M140 S{bed_temp} ; setting bed temp and continue
       M104 S{hotend_temp} ; set nozzle temp and continue
       M190 S{bed_temp} ; block for bed temp
       M109 S{hotend_temp} ; block for nozzle temp""")

# home the printer
print("G28 ; homing printer")

if mesh_type != None:
    if mesh_type == 'Duet':
        print("G29 S1 ; loading mesh from Slot 1")
    else:
        print("M420 S1 ; loading mesh from Slot 1")


# nozzle priming
print("""G1 Z15.0 F6000 ; Move the platform down 15mm
G92 E0 ; Reset Extruder
G1 X10.1 Y20 Z0.28 F5000.0 ; Move to start position
G1 X10.1 Y200.0 Z0.28 F1500.0 E15 ; Draw the first line
G1 X10.4 Y200.0 Z0.28 F5000.0 ; Move to side a little
G1 X10.4 Y20 Z0.28 F1500.0 E30 ; Draw the second line
G92 E0 ; Reset Extruder
G1 Z15 ; Lower Z to 15mm
G1 X150 Y150 ; Goto X150 and Y150 for printing
""")

# goto z height
print(f"G1 X{curr_x:.3f} Y{curr_y:.3f} Z{curr_z:.3f} F{(travel_speed * 60):.0f}")

def up():
    global curr_z
    curr_z += layer_height
    print(f"G1 Z{curr_z:.3f}")


def line(x, y, speed):
    length = sqrt(x ** 2 + y ** 2)
    global curr_x, curr_y
    curr_x += x
    curr_y += y
    if speed > 0:
        print(f"G1 X{curr_x:3f} Y{curr_y:.3f} E{(extrusion_for_length(length)):.4f} F{(speed * 60):.0f}")
    else:
        print(f"G1 X{curr_x:3f} Y{curr_y:.3f} F{(travel_speed * 60):0f}")

def goto(x, y):
    global curr_x, curr_y
    curr_x = x + offset_x
    curr_y = y + offset_y
    print(f"G1 X{curr_x:3f} Y{curr_y:3f}")

line(-object_width / 2, 0, 0)

for l in range(2):
    for offset_i in range(5):
        offset = offset_i * extrusion_width
        line(object_width + offset, 0, first_layer_speed)
        line(0, extrusion_width + offset * 2, first_layer_speed)
        line(-object_width - offset * 2, 0, first_layer_speed)
        line(0, -extrusion_width - offset * 2, first_layer_speed)
        line(offset, 0, first_layer_speed)
        line(0, -extrusion_width, 0)
    up()
    goto(-object_width / 2, 0)

segment = (object_width * 1.0) / num_patterns
space = segment - pattern_width

for l in range(layers):
    pressure_advance = (l / (layers * 1.0)) * (pressure_advance_max - pressure_advance_min) + pressure_advance_min
    if l == 2:
        print("M106 S1 ; turn on part cooling fan")
    print(f"; layer {l:d}, pressure advance: {pressure_advance:.3f}")
    if alerting == 'yes':
        print(f"""M117 starting layer {l}")
             M117 Pressure/Linear Advance set to: {pressure_advance}""")
    print(f"M572 D0 S{pressure_advance:.3f}")
    for i in range(num_patterns):
        line(space / 2, 0, fast_speed)
        line(pattern_width, 0, slow_speed)
        line(space / 2, 0, fast_speed)
    line(0, extrusion_width, fast_speed)
    for i in range(num_patterns):
        line(-space / 2, 0, fast_speed)
        line(-pattern_width, 0, slow_speed)
        line(-space / 2, 0, fast_speed)
    line(0, -extrusion_width, fast_speed)
    up()

print("""M106 S0 ; turn off part cooling fan
G91 Z ; set Z to relative position
G1 Z30 ; lower Z to 30
G28 X ; home X
G28 Y ; home Y
M104 S0 ; turn off hotend
M190 S0 ; turn off bed""")