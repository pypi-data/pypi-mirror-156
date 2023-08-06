import math
import numpy as np


def dode_face_dodecahedron_coord(radius):
    # Setup coordinates of 20 verticies when scaler = 1
    scaler = radius/(3**0.5)
    m = (1+5**(0.5))/2
    V1 = [0, m, 1/m]
    V2 = [0, m, -1/m]
    V3 = [0, -m, 1/m]
    V4 = [0, -m, -1/m]
    V5 = [1/m, 0, m]
    V6 = [1/m, 0, -m]
    V7 = [-1/m, 0, m]
    V8 = [-1/m, 0, -m]
    V9 = [m, 1/m, 0]
    V10 = [m, -1/m, 0]
    V11 = [-m, 1/m, 0]
    V12 = [-m, -1/m, 0]
    V13 = [1, 1, 1]
    V14 = [1, 1, -1]
    V15 = [1, -1, 1]
    V16 = [1, -1, -1]
    V17 = [-1, 1, 1]
    V18 = [-1, 1, -1]
    V19 = [-1, -1, 1]
    V20 = [-1, -1, -1]
    coord = [V1, V2, V3, V4, V5, V6, V7, V8, V9, V10,
             V11, V12, V13, V14, V15, V16, V17, V18, V19, V20]
    # calculate coordinates according to the scaler as coord_ (list)
    coord_ = []
    for i in coord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        coord_.append(temp_list)
    return coord_


def dode_face_distance(a, b):
    # a seperated function for calculating the distance between two coordinates
    n = 15
    return round(((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2)**0.5, n)


def dode_face_mid_pt(a, b):
    # this is a seperate function for calculating mid point of two coords
    n = 15
    return [round((a[0]+b[0])/2, n), round((a[1]+b[1])/2, n), round((a[2]+b[2])/2, n)]


def dode_face_COM_coor(a, b, c, d, e):
    # calculate the center of mass(COM) according to 5 coords on the same face
    n = 10
    mid_a = dode_face_mid_pt(c, d)
    mid_b = dode_face_mid_pt(d, e)
    mid_c = dode_face_mid_pt(a, e)
    COM_a = []
    COM_b = []
    COM_c = []
    # calculate 3 COM here and check if they are overlapped
    for i in range(0, 3):
        COM_a.append(round(a[i] + (mid_a[i] - a[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
        COM_b.append(round(b[i] + (mid_b[i] - b[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
        COM_c.append(round(c[i] + (mid_c[i] - c[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
    # checking overlap
    if round(COM_a[0], n) == round(COM_b[0], n) and round(COM_b[0], n) == round(COM_c[0], n) and \
        round(COM_a[1], n) == round(COM_b[1], n) and round(COM_b[1], n) == round(COM_c[1], n) and \
            round(COM_a[2], n) == round(COM_b[2], n) and round(COM_b[2], n) == round(COM_c[2], n):
        return COM_a
    else:
        return COM_a


def dode_face_COM_list_gen(radius):
    # generate the list of COM of all 12 faces
    coord = dode_face_dodecahedron_coord(radius)
    COM_list = []
    COM_list.append(dode_face_COM_coor(
        coord[6], coord[18], coord[2], coord[14], coord[4]))
    COM_list.append(dode_face_COM_coor(
        coord[6], coord[4], coord[12], coord[0], coord[16]))
    COM_list.append(dode_face_COM_coor(
        coord[4], coord[14], coord[9], coord[8], coord[12]))
    COM_list.append(dode_face_COM_coor(
        coord[6], coord[18], coord[11], coord[10], coord[16]))
    COM_list.append(dode_face_COM_coor(
        coord[14], coord[2], coord[3], coord[15], coord[9]))
    COM_list.append(dode_face_COM_coor(
        coord[18], coord[11], coord[19], coord[3], coord[2]))
    COM_list.append(dode_face_COM_coor(
        coord[16], coord[10], coord[17], coord[1], coord[0]))
    COM_list.append(dode_face_COM_coor(
        coord[12], coord[0], coord[1], coord[13], coord[8]))
    COM_list.append(dode_face_COM_coor(
        coord[7], coord[17], coord[10], coord[11], coord[19]))
    COM_list.append(dode_face_COM_coor(
        coord[5], coord[13], coord[8], coord[9], coord[15]))
    COM_list.append(dode_face_COM_coor(
        coord[3], coord[19], coord[7], coord[5], coord[15]))
    COM_list.append(dode_face_COM_coor(
        coord[1], coord[17], coord[7], coord[5], coord[13]))
    return COM_list


def dode_face_COM_leg_coor(a, b, c, d, e):
    # calculate COM and 5 legs of one protein, 6 coords in total [COM, lg1, lg2, lg3, lg4, lg5]
    COM_leg = []
    COM_leg.append(dode_face_COM_coor(a, b, c, d, e))
    COM_leg.append(dode_face_mid_pt(a, b))
    COM_leg.append(dode_face_mid_pt(b, c))
    COM_leg.append(dode_face_mid_pt(c, d))
    COM_leg.append(dode_face_mid_pt(d, e))
    COM_leg.append(dode_face_mid_pt(e, a))
    return COM_leg


def dode_face_COM_leg_list_gen(radius):
    # generate all COM and leg coords of 12 faces as a large list
    coord = dode_face_dodecahedron_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[6], coord[18], coord[2], coord[14], coord[4]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[6], coord[4], coord[12], coord[0], coord[16]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[4], coord[14], coord[9], coord[8], coord[12]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[6], coord[18], coord[11], coord[10], coord[16]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[14], coord[2], coord[3], coord[15], coord[9]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[18], coord[11], coord[19], coord[3], coord[2]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[16], coord[10], coord[17], coord[1], coord[0]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[12], coord[0], coord[1], coord[13], coord[8]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[7], coord[17], coord[10], coord[11], coord[19]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[5], coord[13], coord[8], coord[9], coord[15]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[3], coord[19], coord[7], coord[5], coord[15]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[1], coord[17], coord[7], coord[5], coord[13]))
    return COM_leg_list


def dode_face_leg_reduce(COM, leg, sigma):
    # calculate the recuced length when considering the sigma value
    n = 14
    m = (1+5**(0.5))/2
    angle = 2*math.atan(m)
    red_len = sigma/(2*math.sin(angle/2))
    ratio = 1 - red_len/dode_face_distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], n))
    return leg_red


def dode_face_leg_reduce_coor_gen(radius, sigma):
    # Generating all the coords of COM and legs when sigma exists
    COM_leg_list = dode_face_COM_leg_list_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 5:
            temp_list.append(dode_face_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def dode_face_angle_cal(COM1, leg1, COM2, leg2):
    n = 8
    c1 = np.array(COM1)
    p1 = np.array(leg1)
    c2 = np.array(COM2)
    p2 = np.array(leg2)
    v1 = p1 - c1
    v2 = p2 - c2
    sig1 = p1 - p2
    sig2 = -sig1
    theta1 = round(math.acos(np.dot(v1, sig1) /
                   (np.linalg.norm(v1)*np.linalg.norm(sig1))), n)
    theta2 = round(math.acos(np.dot(v2, sig2) /
                   (np.linalg.norm(v2)*np.linalg.norm(sig2))), n)
    t1 = np.cross(v1, sig1)
    t2 = np.cross(v1, c1)  # n1 = c1 here
    t1_hat = t1/np.linalg.norm(t1)
    t2_hat = t2/np.linalg.norm(t2)
    phi1 = round(math.acos(np.around(np.dot(t1_hat, t2_hat), n)), n)
    t3 = np.cross(v2, sig2)
    t4 = np.cross(v2, c2)  # n2 = c2 here
    t3_hat = t3/np.linalg.norm(t3)
    t4_hat = t4/np.linalg.norm(t4)
    phi2 = round(math.acos(np.around(np.dot(t3_hat, t4_hat), n)), n)
    t1_ = np.cross(sig1, v1)
    t2_ = np.cross(sig1, v2)
    t1__hat = t1_/np.linalg.norm(t1_)
    t2__hat = t2_/np.linalg.norm(t2_)
    omega = round(math.acos(np.around(np.dot(t1__hat, t2__hat), n)), n)
    return theta1, theta2, phi1, phi2, omega


def dode_face_input_coord(radius, sigma):
    coor = dode_face_leg_reduce_coor_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = coor_[0] - coor_[0]
    lg1 = coor_[1] - coor_[0]
    lg2 = coor_[2] - coor_[0]
    lg3 = coor_[3] - coor_[0]
    lg4 = coor_[4] - coor_[0]
    lg5 = coor_[5] - coor_[0]
    n = -coor_[0]
    return COM, lg1, lg2, lg3, lg4, lg5, n


def dode_face(radius, sigma):
    COM, lg1, lg2, lg3, lg4, lg5, n = dode_face_input_coord(radius, sigma)
    coord = dode_face_leg_reduce_coor_gen(radius, sigma)
    theta1, theta2, phi1, phi2, omega = dode_face_angle_cal(
        coord[0][0], coord[0][3], coord[4][0], coord[4][1])

    f = open('parm.inp', 'w')
    f.write(' # Input file (dodecahedron face-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    dode : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    dode(lg1) + dode(lg1) <-> dode(lg1!1).dode(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg2) <-> dode(lg2!1).dode(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg3) + dode(lg3) <-> dode(lg3!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg4) + dode(lg4) <-> dode(lg4!1).dode(lg4!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg5) + dode(lg5) <-> dode(lg5!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg2) <-> dode(lg1!1).dode(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg3) <-> dode(lg1!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg4) <-> dode(lg1!1).dode(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg5) <-> dode(lg1!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg3) <-> dode(lg2!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg4) <-> dode(lg2!1).dode(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg5) <-> dode(lg2!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg3) + dode(lg4) <-> dode(lg3!1).dode(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg3) + dode(lg5) <-> dode(lg3!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg4) + dode(lg5) <-> dode(lg4!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('dode.mol', 'w')
    f.write('##\n')
    f.write('# Dodecahedron (face-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = dode\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('lg4   ' + str(round(lg4[0], 8)) + '   ' +
            str(round(lg4[1], 8)) + '   ' + str(round(lg4[2], 8)) + '\n')
    f.write('lg5   ' + str(round(lg5[0], 8)) + '   ' +
            str(round(lg5[1], 8)) + '   ' + str(round(lg5[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 5\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('com lg4\n')
    f.write('com lg5\n')
    f.write('\n')
