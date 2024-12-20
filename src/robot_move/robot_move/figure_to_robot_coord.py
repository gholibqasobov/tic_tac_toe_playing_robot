CELLS_COORDS = [{'x0': 207, 'y0': 121, 'x1': 298, 'y1': 215},
                {'x0': 298, 'y0': 122, 'x1': 392, 'y1': 216},
                {'x0': 393, 'y0': 123, 'x1': 488, 'y1': 217},
                {'x0': 205, 'y0': 213, 'x1': 296, 'y1': 309},
                {'x0': 298, 'y0': 215, 'x1': 391, 'y1': 311},
                {'x0': 392, 'y0': 216, 'x1': 488, 'y1': 311},
                {'x0': 204, 'y0': 307, 'x1': 295, 'y1': 405},
                {'x0': 296, 'y0': 309, 'x1': 390, 'y1': 407},
                {'x0': 391, 'y0': 311, 'x1': 487, 'y1': 409}]



ROBOT_TARGET_COORDS = {}
HOME_POSE = (130, 0, 0)
# EE coordinates (x, y), z
BOARD_CELL_COORDS = [(303.5, 54.2), (306.5, -4), (310.5, -62),
                     (245, 54.2), (248, -4), (252, -62),
                     (185, 54.2), (188, -4), (192, -62)
                    ]
ROBOT_Z_COORD = 50

FIGURE_COORDS = {'X': (260, 131.23), 'O': (190.82, 131.23)}

for i in range(len(CELLS_COORDS)):
    cell = CELLS_COORDS[i]
    midpoint = ((cell['x0'] + cell['x1'])/2, (cell['y0'] + cell['y1'])/2)
    ROBOT_TARGET_COORDS[(str(midpoint))] = BOARD_CELL_COORDS[i]

for key, value in ROBOT_TARGET_COORDS.items():
    print(key, '->', value)


# for key, value in FIGURE_COORDS.items():
#     print(key, '->', value)