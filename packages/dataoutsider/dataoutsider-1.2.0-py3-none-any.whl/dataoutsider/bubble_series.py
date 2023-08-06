# bubble_series.py
# by Nick Gerend

from math import sin, pi, cos, sqrt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

class point:
    def __init__(self, item, x, y, A, group, path=0, xo=0, yo=0): 
        self.item = item
        self.x = x
        self.y = y
        self.A = A
        self.group = group
        self.path = path
        self.xo = xo
        self.yo = yo
    def to_dict(self):
        return {
            'item' : self.item,
            'x' : self.x,
            'y' : self.y,
            'A' : self.A,
            'group' : self.group,
            'path' : self.path,
            'xo' : self.xo,
            'yo' : self.yo }

def circle(id, xo, yo, r=1., points=50):
    if points % 2 != 0:
        points += 1
    list_ixyp = []
    angle = -90.
    path_i = 1
    for i in range(points+1):
        # id, x, y, path
        list_ixyp.append((id, xo+r*sin(angle*pi/180.), yo+r*cos(angle*pi/180.), path_i))
        angle += 1./points*360.
        path_i += 1
    list_ixyp.append((id, xo+r*sin(-90.*pi/180.), yo+r*cos(-90.*pi/180.), path_i))
    return list_ixyp

def circle_collide(x1, y1, x2, r1, r2, place='top'):
    y2 = None
    if (x1-r1 < x2-r2 and x1+r1 > x2-r2) or (x1-r1 < x2+r2 and x1+r1 > x2+r2):
        if place == 'bottom':
            y2 = y1 - sqrt(-x2**2 + 2*x2*x1 + r2**2 + 2*r2*r1 + r1**2 - x1**2)
        if place == 'top':
            y2 = sqrt(-x2**2 + 2*x2*x1 + r2**2 + 2*r2*r1 + r1**2 - x1**2) + y1
    return y2

def circle_collided(x1, y1, x2, y2, r1, r2):
    A = (x2-x1)**2 + (y2-y1)**2
    B = (r1+r2)**2
    result = False
    tol = 10
    if round(A, tol) < round(B, tol):
        result = True
    return result
        
def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)

def bubble_group(df):
    dfi = df[['item', 'Min', 'Max']]
    records = dfi.to_records(index=False)
    list_c = list(records)
    group = 0
    groups = {}
    groups[group] = [list_c[0]]
    pop_list = []
    minx = list_c[0][1]
    maxx = list_c[0][2]
    list_c.pop(0)
    while len(list_c) > 0:
        for i in range(len(list_c)):
            minx2 = list_c[i][1]
            maxx2 = list_c[i][2]
            c1 = minx < minx2 and maxx > minx2
            c2 = minx < maxx2 and maxx > maxx2
            c3 = minx2 < minx and maxx2 > minx
            c4 = minx2 < maxx and maxx2 > maxx
            if c1 or c2 or c3 or c4:
                if minx2 < minx:
                    minx = minx2
                if maxx2 > maxx:
                    maxx = maxx2
                groups[group].append(list_c[i])
                pop_list.append(i)
        if len(pop_list) == 0:
            group += 1
            minx = list_c[0][1]
            maxx = list_c[0][2]
            groups[group] = [list_c[0]]
            list_c.pop(0)
        else:
            delete_multiple_element(list_c, pop_list)
            pop_list = []

    rows = []
    for key in groups:
        for i in range(len(groups[key])):
            rows.append((key,groups[key][i][0]))

    df_join = pd.DataFrame(rows, columns=['group', 'item'])
    df_out = df.merge(df_join, on=['item'], how='left')
    return df_out

def bubble_series_calc(df, item_col_name, position_col_name, size_col_name, r_buffer=0.0):
    df['item'] = df[item_col_name]
    df['x'] = df[position_col_name]
    df['A'] = df[size_col_name]
    df['Ao'] = df['A']
    df['r'] = np.sqrt(df['A']/pi) + r_buffer
    df['A'] = pi*df['r']**2
    df['Min'] = -df['r'] + df['x']
    df['Max'] = df['r'] + df['x']
    df = bubble_group(df)
    df_grouped = df.groupby(['group'])
    list_xy = []
    dict_groups = {}
    group_i = 0
    for group, rows in df_grouped:
        if group == 9:
            test = 'debug'
        rows_sort = rows.sort_values(by=['A'], ascending=False)
        for i, row in rows_sort.iterrows():
            item = row['item']
            x = row['x']
            r = row['r']
            A = row['A']
            y = 0.
            if group == 4 and group_i == 4:
                test = 'debug'
            if group_i == 0:
                dict_groups[group] = [(x,0.,r)]
                list_xy.append(point(item, x, 0., A, group))
            else:
                maxy = 0.
                miny = 0.
                yi = 0.
                for j in range(len(dict_groups[group])):
                    #try top and bottom of every prior-placed item
                    #place if no collision and minimum y-extent
                    xo = dict_groups[group][j][0]
                    yo = dict_groups[group][j][1]
                    ro = dict_groups[group][j][2]
                    yt = circle_collide(xo, yo, x, ro, r, place='top')
                    if yt == None:
                        if j == 0:
                            ylast = 0.
                        continue
                    yb = circle_collide(xo, yo, x, ro, r, place='bottom')
                    # check collion against every other placed item
                    ytest = [yt,yb]
                    collided = False
                    for k in range(len(dict_groups[group])):
                        xk = dict_groups[group][k][0]
                        yk = dict_groups[group][k][1]
                        rk = dict_groups[group][k][2]
                        if circle_collided(xk, yk, x, yt, rk, r):
                            ytest[0] = None
                        if circle_collided(xk, yk, x, yb, rk, r):
                            ytest[1] = None
                        if ytest[0] == None and ytest[1] == None:
                            collided = True
                            break
                    if collided:
                        continue
                    if ytest[0] == None:
                        yi = yb
                    elif ytest[1] == None:
                        yi = yt
                    else:
                        if abs(yt) > abs(yb):
                            yi = yb
                        else:
                            yi = yt
                    if j == 0:
                        ylast = yi
                        y = yi
                    elif abs(yi) < abs(ylast) or ylast == 0.:
                        y = yi
                    ylast = yi
                dict_groups[group].append((x,y,r))
                list_xy.append(point(item, x, y, A, group))
            ylast = 0.
            group_i += 1
        group_i = 0

    circles = []
    for i in range(len(list_xy)):
        item = list_xy[i].item
        x = list_xy[i].x
        y = list_xy[i].y
        A = list_xy[i].A
        group = list_xy[i].group
        r = sqrt(A/pi)
        r -= r_buffer
        A = pi*r**2
        circle_i = circle((item,group,A,x,y), x, y, r=r)
        circles.extend(circle_i)

    list_xyc = []
    for i in range(len(circles)):
        item = circles[i][0][0]
        x = circles[i][1]
        y = circles[i][2]
        A = circles[i][0][2]
        path = circles[i][3]
        group = circles[i][0][1]
        xo = circles[i][0][3]
        yo = circles[i][0][4]
        list_xyc.append(point(item, x, y, A, group, path, xo, yo))

    df_out = pd.DataFrame.from_records([s.to_dict() for s in list_xyc])
    return df_out

def bubble_series_plot(bubble_series_calc_df, transparency = 0.5):
    fig, axs = plt.subplots()
    axs.set_aspect('equal', adjustable='box')
    df_group = bubble_series_calc_df.groupby(['item'])
    for group, rows in df_group:
        x = rows['x'].values
        y = rows['y'].values
        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)
        axs.fill(x, y, alpha=transparency, fc=color)
        plt.plot(x, y, 'k-', linewidth=0.5)
    for group, rows in df_group:
        x = rows['x'].values
        y = rows['y'].values
        plt.plot(x, y, 'k-', linewidth=2)
    plt.show()