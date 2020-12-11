import serial
import time

from custom.devices.PhenoBottle.libs.Adafruit_MotorHAT.Adafruit_MotorHAT_Motors import Adafruit_MotorHAT


class Connection:
    def __init__(self, host_address, host_port, motors_address=0x60):
        self.ser = serial.Serial(host_address, host_port)

        # load motors
        MOTOR_INDEX = Adafruit_MotorHAT(addr=motors_address)
        self.mixing_motor = MOTOR_INDEX.getMotor(1)
        self.peristaltic_motor = MOTOR_INDEX.getMotor(2)
        self.bubbling_motor = MOTOR_INDEX.getMotor(3)
        self.light_control = MOTOR_INDEX.getMotor(4)

    def execute_command(self, command):
        self.ser.flush()
        time.sleep(1)
        self.ser.write(command)
        result = self.ser.readline(20)
        decoded_result = str(result[0:len(result) - 2].decode("utf-8"))
        return decoded_result

    def motor_direction(self, motor, direction):
        """
        Starts given motor in given direction.

        :param motor: given motor
        :param direction: True for FORWARD, False for BACKWARD
        """
        motor.run(Adafruit_MotorHAT.FORWARD if direction else Adafruit_MotorHAT.BACKWARD)
        return True

    def motor_stop(self, motor):
        """
        Stops given motor.

        :param motor: given motor
        """
        motor.run(Adafruit_MotorHAT.RELEASE)
        return True

    def motor_speed(self, motor, speed):
        """
        Sets given speed to given motor.

        :param motor: given motor
        :param speed: given speed
        """
        motor.setSpeed(speed)
        return True
