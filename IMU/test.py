import asyncio
from bleak import BleakScanner
from device_model import DeviceModel

BLEDevice_one = None
BLEDevice_two = None

one_rotation = 0
two_rotation = 0

imu_states = {
    "one": {"last_angz": None, "rotation_sum": 0, "rotation": 0},
    "two": {"last_angz": None, "rotation_sum": 0, "rotation": 0},
}

async def scan():
    global BLEDevice_one, BLEDevice_two
    print("Scanning for WT BLE devices...")
    devices = await BleakScanner.discover(timeout=10.0)

    if not devices:
        print("No devices found.")
        return

    for d in devices:
        if d.name and "WT" in d.name:
            print(f"Found: {d.name} | {d.address}")

    lock_input_one = input("Enter MAC address one to connect: ").strip().lower()
    lock_input_two = input("Enter MAC address two to connect: ").strip().lower()

    for d in devices:
        if d.address.lower() == lock_input_one:
            BLEDevice_one = d
        if d.address.lower() == lock_input_two:
            BLEDevice_two = d

def handle_angz_factory(label):
    one_rotation = 0
    two_rotation = 0
    def handle_angz(current_angz):
        state = imu_states[label]
        last_angz = state["last_angz"]

        if last_angz is None:
            state["last_angz"] = current_angz
            return

        delta = current_angz - last_angz

        # Handle wrap-around
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        state["rotation_sum"] += delta
        state["last_angz"] = current_angz

        print(f"[{label}] Current: {current_angz:.2f}, Δ: {delta:.2f}, Accumulated: {state['rotation_sum']:.2f}")

        if abs(state["rotation_sum"]) >= 180:
            print(f"[{label}] 🌀 Full turn detected!")
            
            if (label == "one"):
               one_rotation = 1
            elif (label == "two"):
               two_rotation = 1 
            
            state["rotation"] = 1
            state["rotation_sum"] = 0
    return handle_angz

async def main():
    await scan()
    if BLEDevice_one and BLEDevice_two:
        device_one = DeviceModel("IMU-One", BLEDevice_one, handle_angz_factory("one"))
        device_two = DeviceModel("IMU-Two", BLEDevice_two, handle_angz_factory("two"))

        # Run both devices concurrently
        await asyncio.gather(
            device_one.openDevice(),
            device_two.openDevice()
        )
    else:
        print("One or both BLE devices not selected.")

if __name__ == "__main__":
    asyncio.run(main())
