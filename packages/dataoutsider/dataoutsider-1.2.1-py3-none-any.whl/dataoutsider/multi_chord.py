# multi_chord.py
# by Nick Gerend

import pandas as pd
import numpy as np
from math import sqrt, sin, cos, atan2, pi, isnan
import matplotlib.pyplot as plt
import random
import pkg_resources

def load_olympics_df():
    # data sourced from https://www.kaggle.com/heesoo37/olympic-history-data-a-thorough-analysis/data
    stream = pkg_resources.resource_stream(__name__, 'data/athlete_events.csv')
    return pd.read_csv(stream)

class group:
    def __init__(self, group, element, value, position, offset, x1, x2): 
        self.group = group
        self.element = element
        self.value = value
        self.position = position
        self.offset = offset
        self.x1 = x1
        self.x2 = x2
    def to_dict(self):
        return {
            'group' : self.group,
            'element' : self.element,
            'value' : self.value,
            'position' : self.position,
            'offset' : self.offset,
            'x1' : self.x1, 
            'x2' : self.x2 }

class point:
    def __init__(self, group, value, count, x, y, path, type='chord'): 
        self.group = group
        self.value = value
        self.count = count
        self.x = x
        self.y = y
        self.path = path
        self.type = type
    def to_dict(self):
        return {
            'group' : self.group,
            'value' : self.value,
            'count' : self.count,
            'x' : self.x,
            'y' : self.y,
            'path' : self.path,
            'type' : self.type }

def polarize(x, max_x, y_offset = 0.):
    y = max_x/4.+y_offset
    angle = (2.*pi)*(((x)%(max_x))/(max_x))
    angle_deg = angle * 180./pi
    angle_rotated = (abs(angle_deg-360.)+90.) % 360. 
    angle_new = angle_rotated * pi/180.
    x_out = (y)*cos(angle_new)
    y_out = (y)*sin(angle_new)

    #x_out, y_out = rink_scale(x_out, y_out, 1., 1.) #2.19608

    return x_out, y_out

def LnToPntDst(x0, y0, x1, y1, x2, y2):
    n = abs((y1-y2)*x0+(x2-x1)*y0+x1*y2-x2*y1)
    d = sqrt((x2-x1)**2+(y2-y1)**2)
    return n/d

def DistBtwTwoPnts(x1, y1, x2, y2):
    return sqrt((x2-x1)**2+(y2-y1)**2)

def Rotate(x, y, angledeg, x_offset, y_offset):
    xa = x*cos(angledeg*pi/180) + y*sin(angledeg*pi/180)
    ya = -x*sin(angledeg*pi/180) + y*cos(angledeg*pi/180)
    xa -= x_offset
    ya -= y_offset
    return xa, ya

def AngleByTwoPnts(x1, y1, x2, y2):
    return atan2(x2-x1, y2-y1)*180/pi - 90

def chord(x0, y0, x1, y1, x2, y2, points, h_override=0.):
    h = LnToPntDst(x0, y0, x1, y1, x2, y2)
    w = DistBtwTwoPnts(x1, y1, x2, y2)

    if h_override == 0.:
        new_h = (1.-(h/w)/10.)*h
        if new_h < h*0.01:
            h = h*0.01
        else:
            h = new_h
    else:
        h = h*h_override

    a = AngleByTwoPnts(x1, y1, x2, y2)
    xr = []
    yr = []
    for i in range(points+1):
        arc_percent = i/(points/2.)
        if i > points/2.:
            arc_percent = (points-i)/(points/2.)
        if i == 0 or i == points:
            arc = 0.
        else:
            arc = sqrt((h/2.)**2-((h/2.)-(h/2.)/((points)/2.)*i)**2.)
        percent = arc/(h/2.)

        y_1 = -percent*arc+(1-percent)*arc_percent
        y_2 = percent*arc+(1-percent)*arc_percent
        xr_1, yr_1 = Rotate(i/points*w, y_1, a, -x1, -y1)
        xr_2, yr_2 = Rotate(i/points*w, y_2, a, -x1, -y1)

        d1 =  DistBtwTwoPnts(x0, y0, xr_1, yr_1)
        d2 =  DistBtwTwoPnts(x0, y0, xr_2, yr_2)

        if d1 < d2:
            xr.append(xr_1)
            yr.append(yr_1)
        else:
            xr.append(xr_2)
            yr.append(yr_2)
    return list(zip(xr, yr))
    
def rescale(x, xmin, xmax, newmin, newmax):
    rescaled = (newmax-newmin)*((x-xmin)/(xmax-xmin))+newmin
    return rescaled

def multi_chord_agg(df, order, percent = 100., buffer = 1., elements_offset = 0.04, elements_height = 0.04, group_offset = 0., group_height = 0.04):

    #region initialize element list
    element_list = []
    for i, row in df.iterrows():
        group_i = row['group']
        value_i = row['value']
        elements = group_i.split(',')
        for j in range(len(elements)):
            element_list.append(group(group_i, elements[j], value_i, 0, 0., 0., 0.))
    df_elements = pd.DataFrame.from_records([s.to_dict() for s in element_list])
    #endregion

    #region set up group propperties
    df_group = df_elements.groupby(['element'])['value'].sum().reset_index()
    buffer = buffer/100.*df_group['value'].sum()
    df_group['offset'] = 0.

    order_list = order.split(',')
    df_group['order'] = [order_list.index(x)+1 for x in df_group['element']]
    
    offset = 0.
    for i, row in df_group.sort_values(by=['order'], ascending=True).iterrows():
        df_group.at[i,'offset'] = offset
        offset += row['value']
    dict_group = df_group.set_index('element').T.to_dict('list')
    #endregion

    #region endpoints
    value_offset = 0.
    last_group = order_list[0]
    df_elements['order'] = [order_list.index(x)+1 for x in df_elements['element']]
    for i, row in df_elements.sort_values(by=['order', 'value'], ascending=True).iterrows():
        if row['element'] != last_group:
            value_offset = 0.
            last_group = row['element']
        
        order_i = row['order']
        offset = dict_group[row['element']][1]

        df_elements.at[i,'offset'] = value_offset
        df_elements.at[i,'x1'] = offset + value_offset + buffer*(order_i-1)
        df_elements.at[i,'x2'] = offset + value_offset + row['value'] + buffer*(order_i-1)

        value_offset += row['value']
    #endregion

    #region setup virtual points
    span = df_elements['x2'].max()+buffer

    if percent < 100.:
        span = df_elements['x2'].max()*(1./(percent/100.))

    df_elements_prior = df_elements.copy()
    df_elements_next = df_elements.copy()
    df_elements_prior['x1'] = df_elements_prior['x1'] - span
    df_elements_prior['x2'] = df_elements_prior['x2'] - span
    df_elements_prior['position'] = -1
    df_elements_next['x1'] = df_elements_next['x1'] + span
    df_elements_next['x2'] = df_elements_next['x2'] + span
    df_elements_next['position'] = 1
    dfs = [df_elements_prior, df_elements, df_elements_next]
    df_combined = pd.concat(dfs, axis=0)
    #endregion

    #region point dictionary
    chord_dict = {}
    for name, group_i in df_combined.groupby(['group', 'position']):
        x_list = []
        key = name
        for i, row in group_i.sort_values(by=['order'], ascending=True).iterrows():
            e = row['element']
            x1 = row['x1']
            x2 = row['x2']
            x_list.append([e,x1,x2])
        chord_dict[key] = x_list
    #endregion

    #region select point path
    chord_arc_dict = {}
    for i, row in df.iterrows():
        list_i = chord_dict[row['group'],0]
        list_neg = chord_dict[row['group'],-1]
        list_pos = chord_dict[row['group'],1]

        if len(list_i) > 1:
            list_new = []
            p1 = list_i[0][2]
            p2 = 0.
            for j in range(len(list_i)):

                p1_0 = p1
                if j == len(list_i)-1:
                    j = -1

                p2_i = list_i[j+1][1]
                p2_neg = list_neg[j+1][1]
                p2_pos = list_pos[j+1][1]

                i_delta = abs(p1-p2_i)
                neg_delta = abs(p1-p2_neg)
                pos_delta = abs(p1-p2_pos)

                if i_delta < neg_delta:
                    if i_delta < pos_delta:
                        p2 = p2_i
                        p1 = list_i[j+1][2]
                    else:
                        p2 = p2_pos
                        p1 = list_pos[j+1][2]
                elif pos_delta < neg_delta:
                    p2 = p2_pos
                    p1 = list_pos[j+1][2]
                else:
                    p2 = p2_neg
                    p1 = list_neg[j+1][2]

                list_new.append([row['group'],p1_0, p2])
            chord_arc_dict[row['group']] = list_new
        else:
            chord_arc_dict[row['group']] = list_i
    #endregion

    #region draw point path
    list_xy = []
    for i, row in df.iterrows():
        group_i = row['group']
        value = row['value']
        count = len(group_i.split(','))
        list_path = chord_arc_dict[row['group']]

        if count == 1:
            #region 1 element
            p1 = list_path[0][1]
            p2 = list_path[0][2]
            points = int(abs(p2-p1)/(span)/2.*720)+10
            s1 = np.linspace(p2, p1, num=points)
            path = 1
            for k in range(len(s1)):
                x, y = polarize(s1[k], span)
                list_xy.append(point(group_i, value, count, x, y, path))
                path += 1
            x1, y1 = polarize(p1, span)
            x2, y2 = polarize(p2, span)
            chord_list = chord(0., 0., x1, y1, x2, y2, 20, 0.25)
            for k in range(len(chord_list)):
                list_xy.append(point(group_i, value, count, chord_list[k][0], chord_list[k][1], path))
                path += 1
            #endregion
        
        else:
            #region multiple elements

            #region first straight segment
            path = 1
            p1 = chord_dict[row['group'],0][0][1]
            p2 = list_path[0][1]
            points = int(abs(p2-p1)/(span)/2.*720)
            #straight between p1 to p2
            s1 = np.linspace(p1, p2, num=points)
            for k in range(len(s1)):
                    x, y = polarize(s1[k], span)
                    list_xy.append(point(group_i, value, count, x, y, path))
                    path += 1        
            #endregion
            
            for j in range(len(list_path)):

                #region curves
                p2 = list_path[j][1]
                x1, y1 = polarize(p2, span)
                p3 = list_path[j][2]
                x2, y2 = polarize(p3, span)
                chord_list = chord(0., 0., x1, y1, x2, y2, 50)
                for k in range(len(chord_list)):
                        list_xy.append(point(group_i, value, count, chord_list[k][0], chord_list[k][1], path))
                        path += 1
                #endregion

                #region lagging straight segments
                if j < len(list_path)-1:
                    p4 = list_path[j+1][1]
                    #straight between p3 to p4
                    points = int(abs(p4-p3)/(span)/2.*720)
                    s2 = np.linspace(p3, p4, num=points)
                    for k in range(len(s2)):
                        x, y = polarize(s2[k], span)
                        list_xy.append(point(group_i, value, count, x, y, path))
                        path += 1
                #endregion

            #endregion
    #endregion

    #region rescale to unit radius
    for i in range(len(list_xy)):
        list_xy[i].x = rescale(list_xy[i].x, -span/4., span/4., -1., 1.)
        list_xy[i].y = rescale(list_xy[i].y, -span/4., span/4., -1., 1.)
    #endregion

    #region add legends
    group_offset += elements_offset + elements_height
    for i, row in df_elements.iterrows():
        group_i =  row.group
        value = row.value
        count = len(group_i.split(','))
        element = row.element

        p1 = row.x1
        p2 = row.x2
        points = int(abs(p2-p1)/(span)/2.*720)+3
        
        path = 1
        top = np.linspace(p1, p2, num=points)
        x1 = 0
        y1 = 0
        initial = True
        for k in range(len(top)):
            top_k = rescale(top[k], -span/4., span/4., -1., 1.)
            x, y = polarize(top_k, 4., elements_offset)
            if initial:
                x1 = x
                y1 = y
                initial = False
            list_xy.append(point(group_i, value, count, x, y, path, 'group_'+element))
            path += 1
        bottom = np.linspace(p2, p1, num=points)
        for k in range(len(bottom)):
            bottom_k = rescale(bottom[k], -span/4., span/4., -1., 1.)
            x, y = polarize(bottom_k, 4., elements_offset + elements_height)
            list_xy.append(point(group_i, value, count, x, y, path, 'group_'+element))
            path += 1
        list_xy.append(point(group_i, value, count, x1, y1, path, 'group_'+element))

    for i, row in df_group.iterrows():
        group_i =  row.element
        value = row.value
        count = None

        p1 = row.offset + (row.order-1)*buffer
        p2 = row.offset + row.value + (row.order-1)*buffer
        points = int(abs(p2-p1)/(span)/2.*720)+3
        
        path = 1
        top = np.linspace(p1, p2, num=points)
        x1 = 0
        y1 = 0
        initial = True
        for k in range(len(top)):
            top_k = rescale(top[k], -span/4., span/4., -1., 1.)
            x, y = polarize(top_k, 4., group_offset)
            if initial:
                x1 = x
                y1 = y
                initial = False
            list_xy.append(point(group_i, value, count, x, y, path, 'element'))
            path += 1
        bottom = np.linspace(p2, p1, num=points)
        for k in range(len(bottom)):
            bottom_k = rescale(bottom[k], -span/4., span/4., -1., 1.)
            x, y = polarize(bottom_k, 4., group_offset + group_height)
            list_xy.append(point(group_i, value, count, x, y, path, 'element'))
            path += 1
        list_xy.append(point(group_i, value, count, x1, y1, path, 'element'))
    #endregion

    return list_xy

def multi_chord_groups(df, outer, inner, order=None):
    
    #region outer lookup
    df = df[[outer, inner]]
    group_count = df.groupby(outer)[inner].nunique().reset_index()
    outer_lookup = group_count.sort_values(by=[inner], ascending=False)
    outer_lookup['outer_ID']  = range(1, len(outer_lookup) + 1)
    outer_lookup['outer_ID'] = outer_lookup['outer_ID'].astype(str)
    outer_lookup = outer_lookup.rename({inner: 'e2_count'}, axis=1)
    #endregion

    #region check order:
    if order == None:
        order = ','.join(outer_lookup['outer_ID'].to_list())
    #endregion

    #region merge outer_ID to data
    df = pd.merge(df, outer_lookup, how='left', on=[outer])
    #endregion

    #region create chords
    e2_group = df.groupby(inner)
    chord_dict = {}
    for name, elements in e2_group:
        #collect ordered set of outer by e2
        key = ''
        for i, row in elements.sort_values(by=['outer_ID'], ascending=True).iterrows():
            outer = row['outer_ID']
            key += str(outer) + ','
        key = key[:-1]
        if key in chord_dict:
            chord_dict[key] += 1
        else:
            chord_dict[key] = 1

    df_chord = pd.Series(chord_dict, name='value')
    df_chord.index.name = 'group'
    df_chord = df_chord.reset_index()
    #endregion

    return df_chord, order

def multi_chord_alias(df, outer, inner, percent=100., order=None, buffer = 1., elements_offset = 0.04, elements_height = 0.04, group_offset = 0., group_height = 0.04):
    
    df_chord, order = multi_chord_groups(df, outer, inner, order)
    df_chord['value'] *= 100

    list_xy = multi_chord_agg(df_chord, order, percent, buffer, elements_offset, elements_height, group_offset, group_height)

    df_out = pd.DataFrame.from_records([s.to_dict() for s in list_xy])
    df_out['value'] /= 100

    return df_out

def multi_chord_on_groups_alias(df_chord, percent=100., order=None, buffer = 1., elements_offset = 0.04, elements_height = 0.04, group_offset = 0., group_height = 0.04):
    
    if order == None:
        order_dict = {}
        for i, row in df_chord.iterrows():
            items = row['group'].split(',')
            value = row['value']
            for j in range(len(items)):
                if items[j] in order_dict:
                    order_dict[items[j]] += value
                else:
                    order_dict[items[j]] = value
        df_order = pd.DataFrame(order_dict.items(), columns=['group', 'value'])
        order = df_order.sort_values(by=['value'], ascending=False)['group'].values.tolist()
        order = ",".join(order)
    
    df_chord['value'] *= 100

    list_xy = multi_chord_agg(df_chord, order, percent, buffer, elements_offset, elements_height, group_offset, group_height)

    df_out = pd.DataFrame.from_records([s.to_dict() for s in list_xy])
    df_out['value'] /= 100

    return df_out

def multi_chord_venn(df_mc):
    df_mc_cc = pd.concat([df_mc, df_mc['group'].str.get_dummies(sep=',')], axis = 1)
    df_mc_venn = pd.melt(df_mc_cc, id_vars=['group', 'value'], var_name='group2', value_name='value2')
    return df_mc_venn

def multi_chord_plot(df_mc, level = None, transparency = 0.5):
    max_count = int(max(df_mc['count'].unique()))
    colors = []
    for i in range(max_count):
        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)
        colors.append(color)
    df_lvl_group = df_mc.groupby(['type','group'])
    fig, axs = plt.subplots()
    axs.set_aspect('equal', adjustable='box')
    for group, rows in df_lvl_group:
        x = rows['x'].values
        y = rows['y'].values
        count_check = rows['count'].values[0]
        color = ()
        set_linewidth=0.5
        if isinstance(count_check, (int, float)) and not isnan(count_check):
            color = colors[int(count_check)-1]
            if int(count_check) == level:
                set_linewidth=3
        else:
            r = random.random()
            b = random.random()
            g = random.random()
            color = (r, g, b)
        axs.fill(x, y, alpha=transparency, fc=color)
        plt.plot(x, y, 'k-', linewidth=set_linewidth)
    plt.show(block=True)

def multi_chord_get_alias(df, outer, inner):
    
    #region outer lookup
    df = df[[outer, inner]]
    group_count = df.groupby(outer)[inner].nunique().reset_index()
    outer_lookup = group_count.sort_values(by=[inner], ascending=False)
    outer_lookup['outer_ID']  = range(1, len(outer_lookup) + 1)
    outer_lookup['outer_ID'] = outer_lookup['outer_ID'].astype(str)
    outer_lookup = outer_lookup.rename({inner: 'e2_count'}, axis=1)
    #endregion

    return outer_lookup