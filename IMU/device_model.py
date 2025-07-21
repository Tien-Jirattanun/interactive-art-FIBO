# coding:UTF-8
import time
import asyncio
from bleak import BleakClient

class DeviceModel:
    def __init__(self, deviceName, BLEDevice, callback_method):
        print("Initialize device model")
        self.deviceName = deviceName
        self.BLEDevice = BLEDevice
        self.client = None
        self.writer_characteristic = None
        self.isOpen = False
        self.TempBytes = []
        self.callback_method = callback_method

    async def openDevice(self):
        print("Opening device...")
        async with BleakClient(self.BLEDevice, timeout=15) as client:
            self.client = client
            self.isOpen = True

            target_service_uuid = "0000ffe5-0000-1000-8000-00805f9a34fb"
            target_characteristic_uuid_read = "0000ffe4-0000-1000-8000-00805f9a34fb"
            notify_characteristic = None

            # Find the notification characteristic
            print("Matching services...")
            for service in client.services:
                if service.uuid == target_service_uuid:
                    for char in service.characteristics:
                        if char.uuid == target_characteristic_uuid_read:
                            notify_characteristic = char
                            break

            if notify_characteristic:
                print(f"Characteristic found: {notify_characteristic.uuid}")
                await client.start_notify(notify_characteristic.uuid, self.onDataReceived)

                try:
                    while self.isOpen:
                        await asyncio.sleep(1)
                except asyncio.CancelledError:
                    pass
                finally:
                    await client.stop_notify(notify_characteristic.uuid)
            else:
                print("No matching characteristic found")

    def closeDevice(self):
        self.isOpen = False
        print("Device closed")

    def onDataReceived(self, sender, data):
        tempdata = bytes.fromhex(data.hex())
        for byte in tempdata:
            self.TempBytes.append(byte)
            if len(self.TempBytes) == 1 and self.TempBytes[0] != 0x55:
                self.TempBytes.clear()
                continue
            if len(self.TempBytes) == 2 and self.TempBytes[1] != 0x61:
                self.TempBytes.clear()
                continue
            if len(self.TempBytes) == 20:
                self.processData(self.TempBytes)
                self.TempBytes.clear()

    def processData(self, Bytes):
        if Bytes[1] == 0x61:
            # Extract AngZ only
            AngZ = self.getSignInt16(Bytes[19] << 8 | Bytes[18]) / 32768 * 180
            AngZ = round(AngZ, 3)
            self.callback_method(AngZ)


    @staticmethod
    def getSignInt16(num):
        if num >= 0x8000:
            num -= 0x10000
        return num
