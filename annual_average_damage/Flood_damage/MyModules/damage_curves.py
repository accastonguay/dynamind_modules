__author__ = 'acharett'



'''
Commercial damage ($/m2)
Direct: 65.45x when 0<=x<=2.75; 180 when x > 2.75
Indirect: 22.47x when x < 4.45; 100 when x > 4.45
'''


'''Residential damage, from NRM 2002'''

def res_direct_small(x):
    aweMay2002 = 683.80
    aweNov2002 = 699.40
    aweAverage2002 = (aweMay2002 + aweNov2002)/2.
    aweMay2015 = 1136.90
    adjustment_Factor = aweMay2015/aweAverage2002
    damage = 0
    if 0 <= x < 0.1:
        damage = 905*adjustment_Factor + 9760*adjustment_Factor*x
    elif 0.1 <= x < 0.6:
        damage = 783.2*adjustment_Factor + 10978*adjustment_Factor*x
    elif 0.6 <= x < 1.5:
        damage = 697*adjustment_Factor + 11121.1*adjustment_Factor*x
    elif 1.5 <= x < 1.8:
        damage = 16059*adjustment_Factor + 880*adjustment_Factor*x
    elif 1.8 <= x:
        damage = 17643*adjustment_Factor
    return damage



def res_direct_medium(x):
    aweMay2002 = 683.80
    aweNov2002 = 699.40
    aweAverage2002 = (aweMay2002 + aweNov2002)/2.
    aweMay2015 = 1136.90
    adjustment_Factor = aweMay2015/aweAverage2002

    damage = 0
    if 0 <= x < 0.1:
        damage = 2557*adjustment_Factor + 25580*adjustment_Factor*x
    elif 0.1 <= x < 0.6:
        damage = 3342.2*adjustment_Factor + 17728*adjustment_Factor*x
    elif 0.6 <= x < 1.5:
        damage = 10908.33*adjustment_Factor + 5117.77*adjustment_Factor*x
    elif 1.5 <= x < 1.8:
        damage = 17170*adjustment_Factor + 943.33*adjustment_Factor*x
    elif 1.8 <= x:
        damage = 18868*adjustment_Factor
    return damage


def res_direct_large(x):
    aweMay2002 = 683.80
    aweNov2002 = 699.40
    aweAverage2002 = (aweMay2002 + aweNov2002)/2.
    aweMay2015 = 1136.90
    adjustment_Factor = aweMay2015/aweAverage2002
    damage = 0
    if 0 <= x < 0.1:
        damage = 5873*adjustment_Factor + 58700*adjustment_Factor*x
    elif 0.1 <= x < 0.6:
        damage = 9021.4*adjustment_Factor + 27216*adjustment_Factor*x
    elif 0.6 <= x < 1.5:
        damage = 20734.33*adjustment_Factor + 7694.44*adjustment_Factor*x
    elif 1.5 <= x < 1.8:
        damage = 29816*adjustment_Factor + 1640*adjustment_Factor*x
    elif 1.8 <= x:
        damage = 32768*adjustment_Factor
    return damage

'''Commercial damage, from MMBW, 1986'''

def comm_direct(x):
    # def direct(x,a):
    aweFeb1985 = 340.1
    aweMay2015 = 1136.90
    adjustment_Factor = aweMay2015/aweFeb1985
    a1_direct = 65.45 * adjustment_Factor
    a2_direct = 180 * adjustment_Factor


    damage = 0
    if 0 <= x < 2.75:
        damage = a1_direct*x
        #damage = a1_direct*x*a
    elif 2.75 <= x:
        damage = a2_direct
        # damage = a2_direct*a
    return damage

def comm_indirect(x):
    # def direct(x,a):
    aweFeb1985 = 340.1
    aweMay2015 = 1136.90
    adjustment_Factor = aweMay2015/aweFeb1985
    a1_indirect = 22.47 * adjustment_Factor
    a2_indirect = 100 * adjustment_Factor
    damage = 0

    if 0 <= x < 4.45:
        damage = a1_indirect*x
        #damage = a1_direct*x*a
    elif 4.45 <= x:
        damage = a2_indirect
        # damage = a2_direct*a
    return damage

def public_utilities(area):
    aweFeb1985 = 340.1
    aweMay2015 = 1136.90
    adjustment_Factor = aweMay2015/aweFeb1985
    damage = area*270000*adjustment_Factor
    return damage

def amenities(area):
    aweFeb1985 = 340.1
    aweMay2015 = 1136.90
    adjustment_Factor = aweMay2015/aweFeb1985
    damage = area*9300*adjustment_Factor
    return damage

def vehicles(rp, ip):
    # rp = residential properties flooded by more than 0.5 m
    # ip = Industrial and commercial properties flooded by more than 0.5 m
    aweFeb1985 = 340.1
    aweMay2015 = 1136.90
    adjustment_Factor = aweMay2015/aweFeb1985
    damage = 2000*(1.4*rp + 2*ip)*adjustment_Factor
    return damage