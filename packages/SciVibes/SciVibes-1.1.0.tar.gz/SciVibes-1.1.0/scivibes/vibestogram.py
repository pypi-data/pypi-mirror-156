import numpy as np
import matplotlib.pyplot as plt

def plot_vibestogram(vibes):

    # get the vibes in a format matplotlib can understand
    vibenames = []
    vibescores = []

    for vibe in vibes:
        vibenames.append(vibe[0])
        vibescores.append(vibe[1])

    color_samples = {'geeky': {'High': (24,106,59), 'Med': (46,204,113), 'Low': (213, 245, 227)},
                    'fantasy': {'High': (74, 35, 90), 'Med': (165, 105, 189), 'Low': (232, 218, 239)},
                    'anarcho-capitalist': {'High': (66, 73, 73), 'Med': (127, 140, 141), 'Low': (242, 244, 244)},
                    'cursed': {'High': (176, 58, 46), 'Med': (231, 76, 60), 'Low': (245, 183, 177)},
                    'musical': {'High': (81, 46, 95), 'Med': (155, 89, 182), 'Low': (215, 189, 226)},
                    'skater': {'High': (21, 67, 96), 'Med': (41, 128, 185), 'Low': (169, 204, 227)},
                    'cute': {'High': (245, 101, 201), 'Med': (243, 152, 216), 'Low': (248, 194, 232)},
                    'Disney': {'High': (40, 116, 166), 'Med': (93, 173, 226), 'Low': (174, 214, 241)},
                    'jock': {'High': (175, 96, 26), 'Med': (230, 126, 34), 'Low': (245, 203, 167)},
                    'dramatic': {'High': (243, 156, 18), 'Med': (248, 196, 113), 'Low': (250, 215, 160)},
                    'British': {'High': (146, 43, 33), 'Med': (205, 97, 85), 'Low': (230, 176, 170)},
                    'funny': {'High': (241, 196, 15), 'Med': (247, 220, 111), 'Low': (249, 231, 159)},
                    'random': {'High': (46, 64, 83), 'Med': (93, 109, 126), 'Low': (174, 182, 191)},
                    'anime': {'High': (11, 83, 69), 'Med': (22, 160, 133), 'Low': (115, 198, 182)},
                    'gamer': {'High': (14, 98, 81), 'Med': (26, 188, 156), 'Low': (163, 228, 215)}}

    # get the right bar colors
    barcolors = []

    for vibe in vibenames:
        barcolors.append(np.asarray(color_samples[vibe]['Med'])/255)

    pos = np.arange(len(vibenames))
    width = 1.0

    fig, ax = plt.subplots(1, figsize=(16, 8))
    ax.barh(vibenames, vibescores, width, color=barcolors, edgecolor='black')

    # turn off the right spine/ticks
    #ax.spines['right'].set_color('none')
    #ax.yaxis.tick_left()

    # set the y-spine
    #ax.spines['bottom'].set_position('zero')

    # turn off the top spine/ticks
    #ax.spines['top'].set_color('none')
    #ax.xaxis.tick_bottom()

    for tick in ax.get_xticklabels():
        tick.set_rotation(90)

    #plt.setp(ax.xaxis.get_majorticklabels(), ha='right')    

    fig.suptitle("vibe check!! your total vibes")

    fig.savefig("vibestogram.jpg")

    return fig, ax