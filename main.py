import sys
import asyncio
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, QTimer, pyqtSignal, QThread
from PyQt5.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyController, QLowEnergyService
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout, QLabel, QFileDialog
from bleak import BleakClient
from qasync import QEventLoop, asyncSlot

from status import BluetoothWorker

from ArrayBuild import array_build  # Importa la funzione array_build dal modulo ArrayBuild


# Bluetooth configuration
MAC_Laser = "48:87:2D:64:F9:32"
status_UUID = "0000FFE1-0000-1000-8000-00805f9b34fb"
write_UUID = "0000FFE2-0000-1000-8000-00805f9b34fb"
status_request_B = bytes.fromhex("246b000200002a")
status_request_E = bytes.fromhex("246e000200002a")
status_request_F = bytes.fromhex("246f000200002a")


class CustomDialog(QtWidgets.QDialog):
    def __init__(self, hex_string, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HEX-Packet Built")

        # Creare un layout verticale
        layout = QtWidgets.QVBoxLayout(self)

        # Creare un QTextEdit per visualizzare il testo
        text_edit = QtWidgets.QTextEdit(self)
        text_edit.setText(hex_string)
        text_edit.setReadOnly(True)  # Rendere il QTextEdit di sola lettura
        layout.addWidget(text_edit)

        # Aggiungere un pulsante OK
        ok_button = QtWidgets.QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

class BluetoothWorker(QThread):
    result_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.loop = None
        self.client = None
        self.status_dictionary = {
            'status_infoB': {'sender': None, 'data_hex': None},
            'status_infoE': {'sender': None, 'data_hex': None},
            'status_infoF': {'sender': None, 'data_hex': None}
        }
        self.status = 0

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.bluetooth_task())

    async def bluetooth_task(self):
        try:
            async with BleakClient(MAC_Laser) as self.client:
                await self.client.write_gatt_char(status_UUID, status_request_B)
                await self.client.start_notify(status_UUID, self.notification_handler)
                await asyncio.sleep(1)
                await self.client.stop_notify(status_UUID)

                self.status = 1
                await self.client.write_gatt_char(status_UUID, status_request_E)
                await self.client.start_notify(status_UUID, self.notification_handler)
                await asyncio.sleep(1)
                await self.client.stop_notify(status_UUID)

                self.status = 2
                await self.client.write_gatt_char(status_UUID, status_request_F)
                await self.client.start_notify(status_UUID, self.notification_handler)
                await asyncio.sleep(1)
                await self.client.stop_notify(status_UUID)

                # Emit the final status dictionary
                self.result_signal.emit(self.status_dictionary)
        except Exception as e:
            self.error_signal.emit(f"Connection error: {e}")

    def notification_handler(self, sender: int, data: bytearray):
        data_hex = data.hex()
        if self.status == 0:
            self.status_dictionary['status_infoB']['sender'] = sender
            self.status_dictionary['status_infoB']['data_hex'] = data_hex
        elif self.status == 1:
            self.status_dictionary['status_infoE']['sender'] = sender
            self.status_dictionary['status_infoE']['data_hex'] = data_hex
        elif self.status == 2:
            self.status_dictionary['status_infoF']['sender'] = sender
            self.status_dictionary['status_infoF']['data_hex'] = data_hex


class StatusWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Status Window')

        main_layout = QVBoxLayout()

        # Add fields for displaying parsed data
        data_layout = QVBoxLayout()
        self.add_data_field(data_layout, "Frequency [kHz]:", "freq")
        self.add_data_field(data_layout, "Power [%]:", "power")
        self.add_data_field(data_layout, "Pulse [ns]:", "pulse")
        self.add_data_field(data_layout, "Lights:", "lights")
        self.add_data_field(data_layout, "Pump Temperature [°C]:", "pump_temp")
        self.add_data_field(data_layout, "TEC Temperature [°C]:", "tec_temp")
        self.add_data_field(data_layout, "Alarm Low Current:", "alarm_low_current")

        self.setWindowIcon(QIcon('C:/Users/tommaso.bernasconi/PycharmProjects/PyQt_BLECommunication/lasericon.png'))
        main_layout.addLayout(data_layout)
        self.setLayout(main_layout)

    def add_data_field(self, layout, label_text, attribute):
        hbox = QHBoxLayout()
        label = QLabel(label_text, self)
        edit = QLineEdit(self)
        edit.setReadOnly(True)
        setattr(self, f"{attribute}_edit", edit)
        hbox.addWidget(label)
        hbox.addWidget(edit)
        layout.addLayout(hbox)

    def update_data_fields(self, status_dictionary):
        if 'status_infoE' in status_dictionary:
            data_hex = status_dictionary['status_infoE']['data_hex']
            freq1 = data_hex[8:10]
            freq2 = data_hex[10:12]
            freq3 = freq2 + freq1
            freq = int(freq3, 16)
            self.freq_edit.setText(str(freq))

            power = int(data_hex[16:18], 16)
            self.power_edit.setText(str(power))

            pulse1 = data_hex[12:14]
            pulse2 = data_hex[14:16]
            pulse3 = pulse2 + pulse1
            pulse = int(pulse3, 16)
            self.pulse_edit.setText(str(pulse))

            lights = data_hex[18:20]
            if lights == "00":
                lights_s = "No lights on"
            elif lights == "01":
                lights_s = "Button pressed, no laser"
            elif lights == "03":
                lights_s = "LASER ON"
            elif lights == "04":
                lights_s = "RED LIGHT ON"
            self.lights_edit.setText(lights_s)

            pump_temp = int(data_hex[20:22], 16)
            self.pump_temp_edit.setText(str(pump_temp))

            tec_temp = int(data_hex[22:24], 16)
            self.tec_temp_edit.setText(str(tec_temp))

        if 'status_infoF' in status_dictionary:
            data_hex = status_dictionary['status_infoF']['data_hex']
            lowcurrent = data_hex[16:18]
            if lowcurrent == "01":
                self.alarm_low_current_edit.setText("Alarm: Low Current")
            else:
                self.alarm_low_current_edit.setText("No Alarm")


class MainWindow(QtWidgets.QWidget):
    def __init__(self, mac_address, uuid):
        super().__init__()
        self.init_ui()
        self.discovery_agent = None  # Inizializza l'agente di discovery Bluetooth
        self.controller = None
        self.service = None
        self.hex_string = None

        self.mac_address = mac_address
        self.uuid = uuid

        self.setWindowIcon(QIcon('C:/Users/tommaso.bernasconi/PycharmProjects/PyQt_BLECommunication/lasericon.png'))  # Sostituisci con il percorso della tua icona


    def init_ui(self):
        self.setWindowTitle('CL-100 Laser Cleaner')

        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self)

        # Create grid layout
        grid_layout = QtWidgets.QGridLayout()

        # Create input fields with default values
        self.profile_combo = QtWidgets.QComboBox()
        self.profile_combo.addItems(['Profile 1', 'Profile 2', 'Profile 3', 'Profile 4'])

        self.power_input = QtWidgets.QLineEdit('100')  # Default value set here
        self.frequency_input = QtWidgets.QLineEdit('50')
        self.pulse_input = QtWidgets.QLineEdit('1')
        self.open_delay_input = QtWidgets.QLineEdit('0')
        self.close_delay_input = QtWidgets.QLineEdit('0')
        self.end_delay_input = QtWidgets.QLineEdit('0')
        self.corner_delay_input = QtWidgets.QLineEdit('0')
        self.jump_delay_input = QtWidgets.QLineEdit('0')
        self.x_cal_input = QtWidgets.QLineEdit('0')
        self.y_cal_input = QtWidgets.QLineEdit('0')

        self.graph_combo = QtWidgets.QComboBox()
        self.graph_combo.addItems(['Beeline', 'Rectangle', 'Round', 'Sine', '---', 'Text', 'Spiral', 'Lissajous'])
        self.mode_input = QtWidgets.QCheckBox('Mode')
        self.times_input = QtWidgets.QLineEdit('1')
        self.speed_input = QtWidgets.QLineEdit('100')
        self.focal_length_combo = QtWidgets.QComboBox()
        self.focal_length_combo.addItems(['F163', 'F254', 'F330'])
        self.x_focus_input = QtWidgets.QLineEdit('0')
        self.y_focus_input = QtWidgets.QLineEdit('0')

        self.length_input = QtWidgets.QLineEdit('100')
        self.rect_width_input = QtWidgets.QLineEdit('50')
        self.bee_axis_combo = QtWidgets.QComboBox()
        self.bee_axis_combo.addItems(['X', 'Y'])
        self.ctr_en_input = QtWidgets.QCheckBox('CtrEN')
        self.fill_en_input = QtWidgets.QCheckBox('FillEN')
        self.round_diameter_input = QtWidgets.QLineEdit('0')
        self.sine_length_input = QtWidgets.QLineEdit('100')
        self.sine_margin_input = QtWidgets.QLineEdit('0')
        self.sine_phase_inc_input = QtWidgets.QLineEdit('0')
        self.sine_cycle_count_input = QtWidgets.QLineEdit('1')
        self.text_length_input = QtWidgets.QLineEdit('100')
        self.text_width_input = QtWidgets.QLineEdit('20')
        self.text_space_input = QtWidgets.QLineEdit('5')
        self.polar_dm_input = QtWidgets.QLineEdit('0')
        self.polar_pf_input = QtWidgets.QLineEdit('0')
        self.polar_angle_input = QtWidgets.QLineEdit('0')
        self.liss_length_input = QtWidgets.QLineEdit('100')
        self.liss_width_input = QtWidgets.QLineEdit('50')

        self.fill_one_input = QtWidgets.QCheckBox('FillONE')
        self.method_one_combo = QtWidgets.QComboBox()
        self.method_one_combo.addItems(['Arched', 'Double', 'Single'])
        self.space_one_input = QtWidgets.QLineEdit('10')
        self.angle_one_input = QtWidgets.QLineEdit('0')
        self.fill_two_input = QtWidgets.QCheckBox('FillTWO')
        self.method_two_combo = QtWidgets.QComboBox()
        self.method_two_combo.addItems(['Arched', 'Double', 'Single'])
        self.space_two_input = QtWidgets.QLineEdit('10')
        self.angle_two_input = QtWidgets.QLineEdit('0')

        self.build_button = QtWidgets.QPushButton('Build')
        self.build_button.clicked.connect(self.build_hex_packet)  # Connect Build button to build_hex_packet function

        self.scan_button = QtWidgets.QPushButton('Scan')  # Create Scan button
        self.scan_button.clicked.connect(self.start_discovery)  # Connect Scan button to start_discovery function

        self.get_name_button = QtWidgets.QPushButton('Get Name')  # Create Get Name button
        self.get_name_button.clicked.connect(self.get_device_name)  # Connect Get Name button to get_device_name function

        self.send_button = QtWidgets.QPushButton('Send')  # Create Send button
        self.send_button.clicked.connect(self.send_packet)  # Connect Send button to send_packet function

        self.load_button = QtWidgets.QPushButton('Load Configuration')
        self.load_button.clicked.connect(self.load_configuration)

        self.save_button = QtWidgets.QPushButton('Save Configuration')
        self.save_button.clicked.connect(self.save_configuration)  # Collega il pulsante alla funzione save_configuration

        # Add widgets to grid layout
        grid_layout.addWidget(QtWidgets.QLabel('Profile'), 0, 0)
        grid_layout.addWidget(self.profile_combo, 0, 1)
        grid_layout.addWidget(QtWidgets.QLabel('Power'), 1, 2)
        grid_layout.addWidget(self.power_input, 1, 3)

        grid_layout.addWidget(QtWidgets.QLabel('Frequency'), 1, 0)
        grid_layout.addWidget(self.frequency_input, 1, 1)
        grid_layout.addWidget(QtWidgets.QLabel('Pulse'), 2, 2)
        grid_layout.addWidget(self.pulse_input, 2, 3)

        grid_layout.addWidget(QtWidgets.QLabel('Open Delay'), 2, 0)
        grid_layout.addWidget(self.open_delay_input, 2, 1)
        grid_layout.addWidget(QtWidgets.QLabel('Close Delay'), 3, 2)
        grid_layout.addWidget(self.close_delay_input, 3, 3)

        grid_layout.addWidget(QtWidgets.QLabel('End Delay'), 3, 0)
        grid_layout.addWidget(self.end_delay_input, 3, 1)
        grid_layout.addWidget(QtWidgets.QLabel('Corner Delay'), 4, 2)
        grid_layout.addWidget(self.corner_delay_input, 4, 3)

        grid_layout.addWidget(QtWidgets.QLabel('Jump Delay'), 4, 0)
        grid_layout.addWidget(self.jump_delay_input, 4, 1)
        grid_layout.addWidget(QtWidgets.QLabel('X CAL'), 5, 2)
        grid_layout.addWidget(self.x_cal_input, 5, 3)

        grid_layout.addWidget(QtWidgets.QLabel('Y CAL'), 5, 0)
        grid_layout.addWidget(self.y_cal_input, 5, 1)

        grid_layout.addWidget(QtWidgets.QLabel('Graph'), 0, 4)
        grid_layout.addWidget(self.graph_combo, 0, 5)
        grid_layout.addWidget(self.mode_input, 0, 7)
        grid_layout.addWidget(QtWidgets.QLabel('Times'), 0, 8)
        grid_layout.addWidget(self.times_input, 0, 9)

        grid_layout.addWidget(QtWidgets.QLabel('Speed'), 1, 4)
        grid_layout.addWidget(self.speed_input, 1, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Focal Length'), 1, 6)
        grid_layout.addWidget(self.focal_length_combo, 1, 7)
        grid_layout.addWidget(QtWidgets.QLabel('X Focus'), 1, 8)
        grid_layout.addWidget(self.x_focus_input, 1, 9)

        grid_layout.addWidget(QtWidgets.QLabel('Y Focus'), 2, 4)
        grid_layout.addWidget(self.y_focus_input, 2, 5)

        grid_layout.addWidget(QtWidgets.QLabel('Length'), 3, 4)
        grid_layout.addWidget(self.length_input, 3, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Rect Width'), 3, 6)
        grid_layout.addWidget(self.rect_width_input, 3, 7)
        grid_layout.addWidget(QtWidgets.QLabel('Bee Axis'), 3, 8)
        grid_layout.addWidget(self.bee_axis_combo, 3, 9)

        grid_layout.addWidget(self.ctr_en_input, 4, 4)
        grid_layout.addWidget(self.fill_en_input, 4, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Round Diameter'), 4, 6)
        grid_layout.addWidget(self.round_diameter_input, 4, 7)

        grid_layout.addWidget(QtWidgets.QLabel('Sine Length'), 5, 4)
        grid_layout.addWidget(self.sine_length_input, 5, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Sine Margin'), 5, 6)
        grid_layout.addWidget(self.sine_margin_input, 5, 7)
        grid_layout.addWidget(QtWidgets.QLabel('Sine Phase Inc'), 5, 8)
        grid_layout.addWidget(self.sine_phase_inc_input, 5, 9)

        grid_layout.addWidget(QtWidgets.QLabel('Sine Cycle Count'), 6, 4)
        grid_layout.addWidget(self.sine_cycle_count_input, 6, 5)

        grid_layout.addWidget(QtWidgets.QLabel('Text Length'), 7, 4)
        grid_layout.addWidget(self.text_length_input, 7, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Text Width'), 7, 6)
        grid_layout.addWidget(self.text_width_input, 7, 7)
        grid_layout.addWidget(QtWidgets.QLabel('Text Space'), 7, 8)
        grid_layout.addWidget(self.text_space_input, 7, 9)

        grid_layout.addWidget(QtWidgets.QLabel('Polar DM'), 8, 4)
        grid_layout.addWidget(self.polar_dm_input, 8, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Polar PF'), 8, 6)
        grid_layout.addWidget(self.polar_pf_input, 8, 7)
        grid_layout.addWidget(QtWidgets.QLabel('Polar Angle'), 8, 8)
        grid_layout.addWidget(self.polar_angle_input, 8, 9)

        grid_layout.addWidget(QtWidgets.QLabel('Liss Length'), 9, 4)
        grid_layout.addWidget(self.liss_length_input, 9, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Liss Width'), 9, 6)
        grid_layout.addWidget(self.liss_width_input, 9, 7)

        grid_layout.addWidget(self.fill_one_input, 10, 4)
        grid_layout.addWidget(self.method_one_combo, 10, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Space One'), 10, 6)
        grid_layout.addWidget(self.space_one_input, 10, 7)
        grid_layout.addWidget(QtWidgets.QLabel('Angle One'), 10, 8)
        grid_layout.addWidget(self.angle_one_input, 10, 9)

        grid_layout.addWidget(self.fill_two_input, 11, 4)
        grid_layout.addWidget(self.method_two_combo, 11, 5)
        grid_layout.addWidget(QtWidgets.QLabel('Space Two'), 11, 6)
        grid_layout.addWidget(self.space_two_input, 11, 7)
        grid_layout.addWidget(QtWidgets.QLabel('Angle Two'), 11, 8)
        grid_layout.addWidget(self.angle_two_input, 11, 9)

        grid_layout.addWidget(self.build_button, 12, 0, 1, 5)
        grid_layout.addWidget(self.scan_button, 12, 5, 1, 5)
        grid_layout.addWidget(self.get_name_button, 13, 0, 1, 5)
        grid_layout.addWidget(self.send_button, 13, 5, 1, 5)
        grid_layout.addWidget(self.load_button, 14, 5, 1, 5)
        grid_layout.addWidget(self.save_button, 14, 0, 1, 5)

        # Add button to open status window
        self.status_button = QtWidgets.QPushButton('Status Window')
        self.status_button.clicked.connect(self.open_status_window)
        grid_layout.addWidget(self.status_button, 15, 0, 1, 10)  # Adjust position in the grid

        # Add list for found devices
        self.devices_list = QtWidgets.QListWidget()
        grid_layout.addWidget(self.devices_list, 16, 0, 1, 10)

        # Add QLineEdit to display device name
        self.device_name_display = QtWidgets.QLineEdit()
        self.device_name_display.setReadOnly(True)  # Make read-only
        grid_layout.addWidget(QtWidgets.QLabel('Device Name'), 17, 0)
        grid_layout.addWidget(self.device_name_display, 17, 1, 1, 9)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    def build_hex_packet(self):
        profile = self.profile_combo.currentText()
        power = self.power_input.text()
        frequency = self.frequency_input.text()
        pulse = self.pulse_input.text()
        open_delay = self.open_delay_input.text()
        close_delay = self.close_delay_input.text()
        end_delay = self.end_delay_input.text()
        corner_delay = self.corner_delay_input.text()
        jump_delay = self.jump_delay_input.text()
        x_cal = self.x_cal_input.text()
        y_cal = self.y_cal_input.text()
        graph = self.graph_combo.currentText()
        mode = self.mode_input.isChecked()
        times = self.times_input.text()
        speed = self.speed_input.text()
        focal_length = self.focal_length_combo.currentText()
        x_focus = self.x_focus_input.text()
        y_focus = self.y_focus_input.text()
        length = self.length_input.text()
        rect_width = self.rect_width_input.text()
        bee_axis = self.bee_axis_combo.currentText()
        ctr_en = self.ctr_en_input.isChecked()
        fill_en = self.fill_en_input.isChecked()
        round_diameter = self.round_diameter_input.text()
        sine_length = self.sine_length_input.text()
        sine_margin = self.sine_margin_input.text()
        sine_phase_inc = self.sine_phase_inc_input.text()
        sine_cycle_count = self.sine_cycle_count_input.text()
        text_length = self.text_length_input.text()
        text_width = self.text_width_input.text()
        text_space = self.text_space_input.text()
        polar_dm = self.polar_dm_input.text()
        polar_pf = self.polar_pf_input.text()
        polar_angle = self.polar_angle_input.text()
        liss_length = self.liss_length_input.text()
        liss_width = self.liss_width_input.text()
        fill_one = self.fill_one_input.isChecked()
        method_one = self.method_one_combo.currentText()
        space_one = self.space_one_input.text()
        angle_one = self.angle_one_input.text()
        fill_two = self.fill_two_input.isChecked()
        method_two = self.method_two_combo.currentText()
        space_two = self.space_two_input.text()
        angle_two = self.angle_two_input.text()

        # Call array_build function
        result_array = array_build(graph, [profile, 0], [power, frequency, pulse, open_delay, close_delay, end_delay,
                                                         corner_delay, jump_delay, x_cal, y_cal],
                                   [graph, mode, times, speed, focal_length, x_focus, y_focus],
                                   [length, rect_width, bee_axis, ctr_en, fill_en, round_diameter, sine_length,
                                    sine_margin, sine_phase_inc, sine_cycle_count, text_length, text_width,
                                    text_space, polar_dm, polar_pf, polar_angle, liss_length, liss_width],
                                   [fill_one, method_one, space_one, angle_one, fill_two, method_two, space_two,
                                    angle_two])

        self.hex_string = result_array[1]  # Save the hex string
        # QtWidgets.QMessageBox.information(self, "HEX-Packet Built", f"HEX-Packet Built: {self.hex_string}")
        dialog = CustomDialog(self.hex_string, self)
        dialog.exec_()

    def load_configuration(self):
        # Apri una finestra di dialogo per selezionare un file di configurazione
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Configuration File", "",
                                                   "Text Files (*.txt);;All Files (*)", options=options)

        if file_path:
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            key, value = line.split('=')
                            # Mappa le chiavi ai widget della GUI
                            if key == "Profile":
                                self.profile_combo.setCurrentText(value)
                            elif key == "Power":
                                self.power_input.setText(value)
                            elif key == "Frequency":
                                self.frequency_input.setText(value)
                            elif key == "Pulse":
                                self.pulse_input.setText(value)
                            elif key == "Open Delay":
                                self.open_delay_input.setText(value)
                            elif key == "Close Delay":
                                self.close_delay_input.setText(value)
                            elif key == "End Delay":
                                self.end_delay_input.setText(value)
                            elif key == "Corner Delay":
                                self.corner_delay_input.setText(value)
                            elif key == "Jump Delay":
                                self.jump_delay_input.setText(value)
                            elif key == "X CAL":
                                self.x_cal_input.setText(value)
                            elif key == "Y CAL":
                                self.y_cal_input.setText(value)
                            elif key == "Graph":
                                self.graph_combo.setCurrentText(value)
                            elif key == "Mode":
                                self.mode_input.setChecked(value.lower() == 'true')
                            elif key == "Times":
                                self.times_input.setText(value)
                            elif key == "Speed":
                                self.speed_input.setText(value)
                            elif key == "Focal Length":
                                self.focal_length_combo.setCurrentText(value)
                            elif key == "X Focus":
                                self.x_focus_input.setText(value)
                            elif key == "Y Focus":
                                self.y_focus_input.setText(value)
                            elif key == "Length":
                                self.length_input.setText(value)
                            elif key == "Rect Width":
                                self.rect_width_input.setText(value)
                            elif key == "Bee Axis":
                                self.bee_axis_combo.setCurrentText(value)
                            elif key == "CtrEN":
                                self.ctr_en_input.setChecked(value.lower() == 'true')
                            elif key == "FillEN":
                                self.fill_en_input.setChecked(value.lower() == 'true')
                            elif key == "Round Diameter":
                                self.round_diameter_input.setText(value)
                            elif key == "Sine Length":
                                self.sine_length_input.setText(value)
                            elif key == "Sine Margin":
                                self.sine_margin_input.setText(value)
                            elif key == "Sine Phase Inc":
                                self.sine_phase_inc_input.setText(value)
                            elif key == "Sine Cycle Count":
                                self.sine_cycle_count_input.setText(value)
                            elif key == "Text Length":
                                self.text_length_input.setText(value)
                            elif key == "Text Width":
                                self.text_width_input.setText(value)
                            elif key == "Text Space":
                                self.text_space_input.setText(value)
                            elif key == "Polar DM":
                                self.polar_dm_input.setText(value)
                            elif key == "Polar PF":
                                self.polar_pf_input.setText(value)
                            elif key == "Polar Angle":
                                self.polar_angle_input.setText(value)
                            elif key == "Liss Length":
                                self.liss_length_input.setText(value)
                            elif key == "Liss Width":
                                self.liss_width_input.setText(value)
                            elif key == "FillONE":
                                self.fill_one_input.setChecked(value.lower() == 'true')
                            elif key == "MethodONE":
                                self.method_one_combo.setCurrentText(value)
                            elif key == "SpaceONE":
                                self.space_one_input.setText(value)
                            elif key == "AngleONE":
                                self.angle_one_input.setText(value)
                            elif key == "FillTWO":
                                self.fill_two_input.setChecked(value.lower() == 'true')
                            elif key == "MethodTWO":
                                self.method_two_combo.setCurrentText(value)
                            elif key == "SpaceTWO":
                                self.space_two_input.setText(value)
                            elif key == "AngleTWO":
                                self.angle_two_input.setText(value)
            except FileNotFoundError:
                QtWidgets.QMessageBox.critical(self, "Error", "Configuration file not found.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while loading the configuration: {e}")

    def save_configuration(self):
        # Apri una finestra di dialogo per selezionare un file di salvataggio
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Configuration File", "",
                                                   "Text Files (*.txt);;All Files (*)", options=options)

        if file_path:
            try:
                with open(file_path, 'w') as file:
                    # Salva i valori dei widget nel file
                    file.write(f"Profile={self.profile_combo.currentText()}\n")
                    file.write(f"Power={self.power_input.text()}\n")
                    file.write(f"Frequency={self.frequency_input.text()}\n")
                    file.write(f"Pulse={self.pulse_input.text()}\n")
                    file.write(f"Open Delay={self.open_delay_input.text()}\n")
                    file.write(f"Close Delay={self.close_delay_input.text()}\n")
                    file.write(f"End Delay={self.end_delay_input.text()}\n")
                    file.write(f"Corner Delay={self.corner_delay_input.text()}\n")
                    file.write(f"Jump Delay={self.jump_delay_input.text()}\n")
                    file.write(f"X CAL={self.x_cal_input.text()}\n")
                    file.write(f"Y CAL={self.y_cal_input.text()}\n")
                    file.write(f"Graph={self.graph_combo.currentText()}\n")
                    file.write(f"Mode={str(self.mode_input.isChecked()).capitalize()}\n")
                    file.write(f"Times={self.times_input.text()}\n")
                    file.write(f"Speed={self.speed_input.text()}\n")
                    file.write(f"Focal Length={self.focal_length_combo.currentText()}\n")
                    file.write(f"X Focus={self.x_focus_input.text()}\n")
                    file.write(f"Y Focus={self.y_focus_input.text()}\n")
                    file.write(f"Length={self.length_input.text()}\n")
                    file.write(f"Rect Width={self.rect_width_input.text()}\n")
                    file.write(f"Bee Axis={self.bee_axis_combo.currentText()}\n")
                    file.write(f"CtrEN={str(self.ctr_en_input.isChecked()).capitalize()}\n")
                    file.write(f"FillEN={str(self.fill_en_input.isChecked()).capitalize()}\n")
                    file.write(f"Round Diameter={self.round_diameter_input.text()}\n")
                    file.write(f"Sine Length={self.sine_length_input.text()}\n")
                    file.write(f"Sine Margin={self.sine_margin_input.text()}\n")
                    file.write(f"Sine Phase Inc={self.sine_phase_inc_input.text()}\n")
                    file.write(f"Sine Cycle Count={self.sine_cycle_count_input.text()}\n")
                    file.write(f"Text Length={self.text_length_input.text()}\n")
                    file.write(f"Text Width={self.text_width_input.text()}\n")
                    file.write(f"Text Space={self.text_space_input.text()}\n")
                    file.write(f"Polar DM={self.polar_dm_input.text()}\n")
                    file.write(f"Polar PF={self.polar_pf_input.text()}\n")
                    file.write(f"Polar Angle={self.polar_angle_input.text()}\n")
                    file.write(f"Liss Length={self.liss_length_input.text()}\n")
                    file.write(f"Liss Width={self.liss_width_input.text()}\n")
                    file.write(f"FillONE={str(self.fill_one_input.isChecked()).capitalize()}\n")
                    file.write(f"MethodONE={self.method_one_combo.currentText()}\n")
                    file.write(f"SpaceONE={self.space_one_input.text()}\n")
                    file.write(f"AngleONE={self.angle_one_input.text()}\n")
                    file.write(f"FillTWO={str(self.fill_two_input.isChecked()).capitalize()}\n")
                    file.write(f"MethodTWO={self.method_two_combo.currentText()}\n")
                    file.write(f"SpaceTWO={self.space_two_input.text()}\n")
                    file.write(f"AngleTWO={self.angle_two_input.text()}\n")

                QtWidgets.QMessageBox.information(self, "Success", "Configuration saved successfully.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while saving the configuration: {e}")


    def start_discovery(self):
        self.devices_list.clear()
        if not self.discovery_agent:
            self.discovery_agent = QBluetoothDeviceDiscoveryAgent()

            # Connect signals
            self.discovery_agent.deviceDiscovered.connect(self.device_discovered)
            self.discovery_agent.finished.connect(self.discovery_finished)

            self.discovery_agent.setLowEnergyDiscoveryTimeout(5000)  # Set timeout for discovery

        self.discovery_agent.start(QBluetoothDeviceDiscoveryAgent.LowEnergyMethod)

    def device_discovered(self, info):
        device_name = info.name()
        if not device_name:
            device_name = "Unnamed"

        address = info.address().toString()
        self.devices_list.addItem(f"{device_name} [{address}]")

    def discovery_finished(self):
        QtWidgets.QMessageBox.information(self, "Bluetooth Discovery", "Discovery finished.")

    def get_device_name(self):
        MAC_Laser = "48:87:2D:64:F9:32"
        # UUID_Service = QBluetoothUuid("00002A00-0000-1000-8000-00805f9b34fb")

        if self.discovery_agent:
            self.discovery_agent.stop()

        self.device_name_display.clear()  # Clear any previous text
        self.device_name_display.setText(f'Searching for device with MAC: {MAC_Laser}')

        self.discovery_agent = QBluetoothDeviceDiscoveryAgent()
        self.discovery_agent.deviceDiscovered.connect(self.check_device)
        self.discovery_agent.finished.connect(self.discovery_finished)
        self.discovery_agent.error.connect(self.scan_error)
        self.discovery_agent.start()

    @pyqtSlot(QBluetoothDeviceInfo)
    def check_device(self, device_info):
        MAC_Laser = "48:87:2D:64:F9:32"
        if device_info.address().toString() == MAC_Laser:
            device_name = device_info.name()
            if not device_name:
                device_name = "Unnamed"
            self.device_name_display.setText(f'Device Name: {device_name}')
            self.discovery_agent.stop()

    def scan_error(self, error):
        # Function to handle Bluetooth scan errors (unchanged)
        pass

    @asyncSlot()
    async def send_packet(self):
        if not hasattr(self, 'hex_string') or not self.hex_string:
            self.append_message("Error: No HEX packet built.")
            return

        byte_array = bytes.fromhex(self.hex_string)
        try:
            async with BleakClient(self.mac_address) as client:
                self.append_message(f"Connected to {self.mac_address}")
                await client.write_gatt_char(self.uuid, byte_array)
                self.append_message(f"Sent: {byte_array}")
        except Exception as e:
            self.append_message(f"Error: {e}")

    def append_message(self, message):
        """Append message to the QListWidget."""
        self.devices_list.addItem(message)  # Use the QListWidget for logging

    def open_status_window(self):
        self.status_window = StatusWindow()
        self.bluetooth_worker = BluetoothWorker()
        self.bluetooth_worker.result_signal.connect(self.status_window.update_data_fields)
        self.bluetooth_worker.error_signal.connect(self.update_text_edit)
        self.bluetooth_worker.start()
        self.status_window.show()

    def update_text_edit(self, message):
        self.text_edit.append(message)


if __name__ == '__main__':
    mac_address = '48:87:2D:64:F9:32'  # Replace with your device's MAC
    uuid = '0000FFE2-0000-1000-8000-00805f9b34fb'  # Replace with your service's UUID

    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    client = MainWindow(mac_address, uuid)
    client.show()
    with loop:
        loop.run_forever()
    sys.exit(app.exec_())
