# status.py
import asyncio
from PyQt5.QtCore import QThread, pyqtSignal
from bleak import BleakClient

# Bluetooth configuration
MAC_Laser = "48:87:2D:64:F9:32"
status_UUID = "0000FFE1-0000-1000-8000-00805f9b34fb"
write_UUID = "0000FFE2-0000-1000-8000-00805f9b34fb"
status_request_B = bytes.fromhex("246b000200002a")
status_request_E = bytes.fromhex("246e000200002a")
status_request_F = bytes.fromhex("246f000200002a")

class BluetoothWorker(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.loop = None
        self.client = None

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

                await self.client.write_gatt_char(status_UUID, status_request_E)
                await self.client.start_notify(status_UUID, self.notification_handler)
                await asyncio.sleep(1)
                await self.client.stop_notify(status_UUID)

                await self.client.write_gatt_char(status_UUID, status_request_F)
                await self.client.start_notify(status_UUID, self.notification_handler)
                await asyncio.sleep(1)
                await self.client.stop_notify(status_UUID)
        except Exception as e:
            self.result_signal.emit(f"Error: {e}")

    def notification_handler(self, sender: int, data: bytearray):
        message = f"Received notification from {sender}: {data.hex()}"
        self.result_signal.emit(message)

