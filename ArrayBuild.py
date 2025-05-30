"""
File: ArrayBuild.py
Author: Tommaso Bernasconi
Date: 09.10.2023

Description: secondary function, from GUI an array is sent with all the settings/parameters stores inside. In this
    function the parameters are being read, translated into HEX-code and linked together to create a single packet.

    !Text-settings are still to be implemented!
"""


def array_build(selected_graph, profile_array, parameter_array, graph_main_array,  graph_2_array, graph_fill_array):
    focus_value = 0
    number_of_inputs = 109
    command_array = ['xx'] * number_of_inputs
    hex_string = ""

    command_array[80] = "00"
    command_array[81] = "00"
    command_array[82] = "00"
    command_array[83] = "00"
    command_array[84] = "00"
    command_array[85] = "00"
    command_array[86] = "00"
    command_array[87] = "00"
    command_array[88] = "00"
    command_array[89] = "00"
    command_array[90] = "00"
    command_array[91] = "00"

    command_array[0] = "24"
    command_array[1] = "c8"
    command_array[2] = "00"
    command_array[3] = "68"
    command_array[108] = "2a"

    command_array[14] = "00"
    command_array[15] = "00"
    command_array[46] = "00"
    command_array[47] = "00"

    for i in range(len(parameter_array)):
        if parameter_array[i] == '':
            parameter_array[i] = "00"
    for i in range(len(graph_main_array)):
        if graph_main_array[i] == '':
            graph_main_array[i] = "00"
    for i in range(len(graph_2_array)):
        if graph_2_array[i] == '':
            graph_2_array[i] = "00"
    for i in range(len(graph_fill_array)):
        if graph_fill_array[i] == '':
            graph_fill_array[i] = "00"

    # Profile %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    command_array[103] = "00"
    if profile_array[0] == "Profile 1":
        command_array[102] = "01"
    elif profile_array[0] == 'Profile 2':
        command_array[102] = "02"
    elif profile_array[0] == "Profile 3":
        command_array[102] = "03"
    elif profile_array[0] == "Profile 4":
        command_array[102] = "04"

    # Parameters %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    hex_power = format(int(parameter_array[0]), '04X')
    command_array[40] = hex_power[2] + hex_power[3]
    command_array[41] = hex_power[0] + hex_power[1]

    hex_frequency = format(int(parameter_array[1]), '04X')
    command_array[42] = hex_frequency[2] + hex_frequency[3]
    command_array[43] = hex_frequency[0] + hex_frequency[1]

    hex_pulse = format(int(parameter_array[2]), '04X')
    command_array[44] = hex_pulse[2] + hex_pulse[3]
    command_array[45] = hex_pulse[0] + hex_pulse[1]

    openDelay = str(int(float(parameter_array[3]) + 1000))
    hex_openDelay = format(int(openDelay), '04X')
    command_array[4] = hex_openDelay[2] + hex_openDelay[3]
    command_array[5] = hex_openDelay[0] + hex_openDelay[1]

    hex_closeDelay = format(int(parameter_array[4]), '04X')
    command_array[6] = hex_closeDelay[2] + hex_closeDelay[3]
    command_array[7] = hex_closeDelay[0] + hex_closeDelay[1]

    hex_endDelay = format(int(parameter_array[5]), '04X')
    command_array[8] = hex_endDelay[2] + hex_endDelay[3]
    command_array[9] = hex_endDelay[0] + hex_endDelay[1]

    hex_cornerDelay = format(int(parameter_array[6]), '04X')
    command_array[10] = hex_cornerDelay[2] + hex_cornerDelay[3]
    command_array[11] = hex_cornerDelay[0] + hex_cornerDelay[1]

    hex_jumpDelay = format(int(parameter_array[7]), '04X')
    command_array[12] = hex_jumpDelay[2] + hex_jumpDelay[3]
    command_array[13] = hex_jumpDelay[0] + hex_jumpDelay[1]

    xCal = str(int(float(parameter_array[8])*1000))
    hex_xCal = format(int(xCal), '04X')
    command_array[104] = hex_xCal[2] + hex_xCal[3]
    command_array[105] = hex_xCal[0] + hex_xCal[1]

    yCal = str(int(float(parameter_array[9])*1000))
    hex_yCal = format(int(yCal), '04X')
    command_array[106] = hex_yCal[2] + hex_yCal[3]
    command_array[107] = hex_yCal[0] + hex_yCal[1]

    # Graphic MAIN %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if graph_main_array[0] == "Beeline":
        graph_main_array[0] = "0"
    elif graph_main_array[0] == "Rectangle":
        graph_main_array[0] = "1"
    elif graph_main_array[0] == "Round":
        graph_main_array[0] = "2"
    elif graph_main_array[0] == "Sine":
        graph_main_array[0] = "3"
    elif graph_main_array[0] == "---":
        graph_main_array[0] = "4"
    elif graph_main_array[0] == "Text":
        graph_main_array[0] = "5"
    elif graph_main_array[0] == "Spiral":
        graph_main_array[0] = "6"
    elif graph_main_array[0] == "Lissajous":
        graph_main_array[0] = "7"
    hex_graph = format(int(graph_main_array[0]), '04X')
    command_array[16] = hex_graph[2] + hex_graph[3]
    command_array[17] = hex_graph[0] + hex_graph[1]

    if graph_main_array[1] == False:
        graph_main_array[1] = "0"
    elif graph_main_array[1] == True:
        graph_main_array[1] = "1"
    hex_mode = format(int(graph_main_array[1]), '04X')
    command_array[18] = hex_mode[2] + hex_mode[3]
    command_array[19] = hex_mode[0] + hex_mode[1]

    hex_times = format(int(graph_main_array[2]), '04X')
    command_array[20] = hex_times[2] + hex_times[3]
    command_array[21] = hex_times[0] + hex_times[1]

    hex_speed = format(int(graph_main_array[3]), '04X')
    command_array[22] = hex_speed[2] + hex_speed[3]
    command_array[23] = hex_speed[0] + hex_speed[1]

    if graph_main_array[4] == "F163":
        graph_main_array[4] = "0"
        focus_value = 5500
    elif graph_main_array[4] == "F254":
        graph_main_array[4] = "1"
        focus_value = 8750
    elif graph_main_array[4] == "F330":
        graph_main_array[4] = "2"
        focus_value = 10000
    hex_focalLength = format(int(graph_main_array[4]), '04X')
    command_array[24] = hex_focalLength[2] + hex_focalLength[3]
    command_array[25] = hex_focalLength[0] + hex_focalLength[1]

    xFocus = str(int(focus_value - (float(graph_main_array[5]) * 100)))
    hex_xFocus = format(int(xFocus), '04X')
    command_array[32] = hex_xFocus[2] + hex_xFocus[3]
    command_array[33] = hex_xFocus[0] + hex_xFocus[1]

    yFocus = str(int(focus_value - (float(graph_main_array[6]) * 100)))
    hex_yFocus = format(int(yFocus), '04X')
    # hex_yFocus = format(int(graph_main_array[6]), '04X')
    command_array[34] = hex_yFocus[2] + hex_yFocus[3]
    command_array[35] = hex_yFocus[0] + hex_yFocus[1]

    # Graphics 2  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    hex_length = format(int(graph_2_array[0]), '04X')
    command_array[26] = hex_length[2] + hex_length[3]
    command_array[27] = hex_length[0] + hex_length[1]

    hex_rectwidth = format(int(graph_2_array[1]), '04X')
    command_array[28] = hex_rectwidth[2] + hex_rectwidth[3]
    command_array[29] = hex_rectwidth[0] + hex_rectwidth[1]

    if graph_2_array[2] == "X":
        graph_2_array[2] = "0"
    elif graph_2_array[2] == "Y":
        graph_2_array[2] = "1"
    hex_direction = format(int(graph_2_array[2]), '04X')
    command_array[30] = hex_direction[2] + hex_direction[3]
    command_array[31] = hex_direction[0] + hex_direction[1]

    if graph_2_array[3] == False:
        graph_2_array[3] = "0"
    elif graph_2_array[3] == True:
        graph_2_array[3] = "1"
    hex_ctrEn = format(int(graph_2_array[3]), '04X')
    command_array[50] = hex_ctrEn[2] + hex_ctrEn[3]
    command_array[51] = hex_ctrEn[0] + hex_ctrEn[1]

    if graph_2_array[4] == False:
        graph_2_array[4] = "0"
    elif graph_2_array[4] == True:
        graph_2_array[4] = "1"
    hex_fillEn = format(int(graph_2_array[4]), '04X')
    command_array[52] = hex_fillEn[2] + hex_fillEn[3]
    command_array[53] = hex_fillEn[0] + hex_fillEn[1]

    hex_rounddiameter = format(int(graph_2_array[5]), '04X')
    command_array[66] = hex_rounddiameter[2] + hex_rounddiameter[3]
    command_array[67] = hex_rounddiameter[0] + hex_rounddiameter[1]

    hex_sinelength = format(int(graph_2_array[6]), '04X')
    command_array[68] = hex_sinelength[2] + hex_sinelength[3]
    command_array[69] = hex_sinelength[0] + hex_sinelength[1]

    hex_sinemargin = format(int(graph_2_array[7]), '04X')
    command_array[70] = hex_sinemargin[2] + hex_sinemargin[3]
    command_array[71] = hex_sinemargin[0] + hex_sinemargin[1]

    hex_cycleCount = format(int(graph_2_array[8]), '04X')
    command_array[72] = hex_cycleCount[2] + hex_cycleCount[3]
    command_array[73] = hex_cycleCount[0] + hex_cycleCount[1]

    hex_phaseInc = format(int(graph_2_array[9]), '04X')
    command_array[48] = hex_phaseInc[2] + hex_phaseInc[3]
    command_array[49] = hex_phaseInc[0] + hex_phaseInc[1]

    hex_textlength = format(int(graph_2_array[10]), '04X')
    command_array[74] = hex_textlength[2] + hex_textlength[3]
    command_array[75] = hex_textlength[0] + hex_textlength[1]

    hex_textwidth = format(int(graph_2_array[11]), '04X')
    command_array[76] = hex_textlength[2] + hex_textlength[3]
    command_array[77] = hex_textlength[0] + hex_textlength[1]

    hex_textspace = format(int(graph_2_array[12]), '04X')
    command_array[78] = hex_textspace[2] + hex_textspace[3]
    command_array[79] = hex_textspace[0] + hex_textspace[1]

    hex_polarDM = format(int(graph_2_array[13]), '04X')
    command_array[92] = hex_polarDM[2] + hex_polarDM[3]
    command_array[93] = hex_polarDM[0] + hex_polarDM[1]

    hex_polarPF = format(int(graph_2_array[14]), '04X')
    command_array[94] = hex_polarPF[2] + hex_polarPF[3]
    command_array[95] = hex_polarPF[0] + hex_polarPF[1]

    hex_polarAngle = format(int(graph_2_array[15]), '04X')
    command_array[96] = hex_polarAngle[2] + hex_polarAngle[3]
    command_array[97] = hex_polarAngle[0] + hex_polarAngle[1]

    hex_lisslength = format(int(graph_2_array[16]), '04X')
    command_array[98] = hex_lisslength[2] + hex_lisslength[3]
    command_array[99] = hex_lisslength[0] + hex_lisslength[1]

    hex_lisswidth = format(int(graph_2_array[17]), '04X')
    command_array[100] = hex_lisslength[2] + hex_lisslength[3]
    command_array[101] = hex_lisslength[0] + hex_lisslength[1]

    # Graphics fill %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    if graph_fill_array[0] == False:
        graph_fill_array[0] = "0"
    elif graph_fill_array[0] == True:
        graph_fill_array[0] = "1"
    hex_fillONE = format(int(graph_fill_array[0]), '04X')
    command_array[54] = hex_fillONE[2] + hex_fillONE[3]
    command_array[55] = hex_fillONE[0] + hex_fillONE[1]

    if graph_fill_array[1] == "Arched":
        graph_fill_array[1] = "1"
    elif graph_fill_array[1] == "Double":
        graph_fill_array[1] = "2"
    elif graph_fill_array[1] == "Single":
        graph_fill_array[1] = "3"
    hex_methodONE = format(int(graph_fill_array[1]), '04X')
    command_array[38] = hex_methodONE[2] + hex_methodONE[3]
    command_array[39] = hex_methodONE[0] + hex_methodONE[1]

    spaceONE = str(int(float(graph_fill_array[2])*100))
    hex_spaceONE = format(int(spaceONE), '04X')
    command_array[36] = hex_spaceONE[2] + hex_spaceONE[3]
    command_array[37] = hex_spaceONE[0] + hex_spaceONE[1]

    hex_angleONE = format(int(graph_fill_array[3]), '04X')
    command_array[58] = hex_angleONE[2] + hex_angleONE[3]
    command_array[59] = hex_angleONE[0] + hex_angleONE[1]

    if graph_fill_array[4] == False:
        graph_fill_array[4] = "0"
    elif graph_fill_array[4] == True:
        graph_fill_array[4] = "1"
    hex_fillTWO = format(int(graph_fill_array[4]), '04X')
    command_array[56] = hex_fillTWO[2] + hex_fillTWO[3]
    command_array[57] = hex_fillTWO[0] + hex_fillTWO[1]

    if graph_fill_array[5] == "Arched":
        graph_fill_array[5] = "1"
    elif graph_fill_array[5] == "Double":
        graph_fill_array[5] = "2"
    elif graph_fill_array[5] == "Single":
        graph_fill_array[5] = "3"
    hex_methodTWO = format(int(graph_fill_array[5]), '04X')
    command_array[64] = hex_methodTWO[2] + hex_methodTWO[3]
    command_array[65] = hex_methodTWO[0] + hex_methodTWO[1]

    spaceTWO = str(int(float(graph_fill_array[6])*100))
    hex_spaceTWO = format(int(spaceTWO), '04X')
    command_array[62] = hex_spaceTWO[2] + hex_spaceTWO[3]
    command_array[63] = hex_spaceTWO[0] + hex_spaceTWO[1]

    hex_angleTWO = format(int(graph_fill_array[7]), '04X')
    command_array[60] = hex_angleTWO[2] + hex_angleTWO[3]
    command_array[61] = hex_angleTWO[0] + hex_angleTWO[1]

    hex_string = ''.join(command_array)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    return command_array, hex_string, xFocus, yFocus

