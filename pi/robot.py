import smbus
import struct
import time

# Currently 46 bytes, stay under 64!
LEDS_LOC       = 0
BUTTONS_LOC    = LEDS_LOC + 3
MOTORS_LOC     = BUTTONS_LOC + 3
BATTERY_LOC    = MOTORS_LOC + 2*2
DISTANCES_LOC  = BATTERY_LOC + 2
PLAY_NOTES_LOC = DISTANCES_LOC + 2*3
ENCODERS_LOC   = PLAY_NOTES_LOC + 1 + 14
READ_GYRO_LOC  = ENCODERS_LOC + 2*2
RESET_GYRO_LOC = TURN_RATE_LOC + 2
CAL_GYRO_LOC   = RESET_GYRO_LOC + 1

class Robot:
    def __init__(self):
        self.bus = smbus.SMBus(1)

    def read_unpack(self, address, size, format):
        self.bus.write_byte(20, address)
        time.sleep(0.0001)
        byte_list = [self.bus.read_byte(20) for _ in range(size)]
        return struct.unpack(format, bytes(byte_list))

    def write_pack(self, address, format, *data):
        data_array = list(struct.pack(format, *data))
        self.bus.write_i2c_block_data(20, address, data_array)
        time.sleep(0.0001)

    def leds(self, red, yellow, green):
        self.write_pack(LEDS_LOC, 'BBB', red, yellow, green)

    def play_notes(self, notes):
        self.write_pack(PLAY_NOTES_LOC, 'B15s', 1, notes.encode("ascii"))

    def motors(self, left, right):
        self.write_pack(MOTORS_LOC, 'hh', left, right)

    def read_buttons(self):
        return self.read_unpack(BUTTONS_LOC, 3, "???")

    def read_battery_millivolts(self):
        return self.read_unpack(BATTERY_LOC, 2, "H")

    def read_distances(self):
        return self.read_unpack(DISTANCES_LOC, 6, "HHH")

    def read_encoders(self):
        return self.read_unpack(ENCODERS_LOC, 4, 'hh')
    
    def read_gyro(self):
        return self.read_unpack(READ_GYRO_LOC, 6, 'IH')
    
    # Not entirely sure this should be B and not ?.
    def reset_gyro(self):
        self.write_pack(RESET_GYRO_LOC, 'B', True)
    
    def calibrate_gyro(self):
        self.write_pack(CAL_GYRO_LOC, 'B', True)