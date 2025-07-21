import asyncio
from bleak import BleakScanner
from device_model import DeviceModel

BLEDevice = None

last_angz = None 
rotation_sum = 0

rotation = 0

async def scan():
    global BLEDevice
    print("Scanning for WT BLE devices...")
    devices = await BleakScanner.discover(timeout=10.0)
    for d in devices:
        if d.name and "WT" in d.name:
            print(f"Found: {d.name} | {d.address}")
    if not devices:
        print("No devices found.")
        return

    lock_input = "B642129E-A384-ED0C-893F-235975A6F543".strip().lower()

    # for custom mac address
    # user_input = input(
    #     "Enter MAC address to connect (e.g. DF:E9:1F:2C:BD:59): ").strip().lower()
    for d in devices:
        if d.address.lower() == lock_input:
            BLEDevice = d
            return

# call back is here
# code right here in this function


def handle_angz(current_angz):

    global last_angz
    global rotation_sum
    global rotation 
    
    rotation = 0

    if last_angz is None:
        last_angz = current_angz
        return

    # Compute difference
    delta = current_angz - last_angz

    # Handle wrap-around (180° -> -180°)
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360

    rotation_sum += delta
    last_angz = current_angz

    print(f"Current Angle: {current_angz:.2f}, Δ: {delta:.2f}, Accumulated: {rotation_sum:.2f}")

    # Detect full turn
    if abs(rotation_sum) >= 180:
        print("🌀 Full turn detected!")
        rotation = 1
        rotation_sum = 0  # Reset for next turn


async def main():
    await scan()
    if BLEDevice:
        device = DeviceModel("MyWT901", BLEDevice, handle_angz)
        await device.openDevice()
    else:
        print("No BLE device selected.")

if __name__ == "__main__":
    asyncio.run(main())
