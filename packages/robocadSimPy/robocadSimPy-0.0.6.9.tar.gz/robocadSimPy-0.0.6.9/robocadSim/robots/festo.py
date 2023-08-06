from .dev import connection


class Festo:
    """
    Class for Festo robot
    """

    def __init__(self):
        self.__right_motor_speed = 0.0
        self.__left_motor_speed = 0.0
        self.__back_motor_speed = 0.0

        self.__right_motor_enc = 0.0
        self.__left_motor_enc = 0.0
        self.__back_motor_enc = 0.0

        self.__reset_right_enc = False
        self.__reset_left_enc = False
        self.__reset_back_enc = False

        self.__reset_imu = False

        self.__ir_1 = 0.0
        self.__ir_2 = 0.0
        self.__ir_3 = 0.0
        self.__ir_4 = 0.0
        self.__ir_5 = 0.0
        self.__ir_6 = 0.0
        self.__ir_7 = 0.0
        self.__ir_8 = 0.0
        self.__ir_9 = 0.0
        self.__imu = 0.0

        self.__grip_servo_pos = 0.0

        self.__motors_channel = connection.TalkPort(65432)
        self.__oms_channel = connection.TalkPort(65433)
        self.__resets_channel = connection.TalkPort(65434)
        self.__encs_channel = connection.ListenPort(65435)
        self.__sensors_channel = connection.ListenPort(65436)

    def connect(self):
        self.__motors_channel.start_talking()
        self.__oms_channel.start_talking()
        self.__resets_channel.start_talking()
        self.__encs_channel.start_listening()
        self.__sensors_channel.start_listening()

    def disconnect(self):
        self.__motors_channel.stop_talking()
        self.__oms_channel.stop_talking()
        self.__resets_channel.stop_talking()
        self.__encs_channel.stop_listening()
        self.__sensors_channel.stop_listening()

    def __update_motors(self):
        self.__motors_channel.out_string = connection.ParseChannels.join_float_channel(
            (
                self.__right_motor_speed,
                self.__left_motor_speed,
                self.__back_motor_speed,
            ))

    def __update_oms(self):
        self.__oms_channel.out_string = connection.ParseChannels.join_float_channel(
            (
                self.__grip_servo_pos,
            ))

    def __update_resets(self):
        self.__resets_channel.out_string = connection.ParseChannels.join_bool_channel(
            (
                self.__reset_right_enc,
                self.__reset_left_enc,
                self.__reset_back_enc,
                self.__reset_imu,
            ))

    def __update_encs(self):
        values = connection.ParseChannels.parse_float_channel(self.__encs_channel.out_string)
        if len(values) == 3:
            self.__right_motor_enc = values[0]
            self.__left_motor_enc = values[1]
            self.__back_motor_enc = values[2]

    def __update_sensors(self):
        values = connection.ParseChannels.parse_float_channel(self.__sensors_channel.out_string)
        if len(values) == 10:
            self.__ir_1 = values[0] * 10
            self.__ir_2 = values[1] * 10
            self.__ir_3 = values[2] * 10
            self.__ir_4 = values[3] * 10
            self.__ir_5 = values[4] * 10
            self.__ir_6 = values[5] * 10
            self.__ir_7 = values[6] * 10
            self.__ir_8 = values[7] * 10
            self.__ir_9 = values[8] * 10
            self.__imu = values[9]

    @property
    def right_motor_speed(self):
        return self.__right_motor_speed

    @right_motor_speed.setter
    def right_motor_speed(self, value):
        self.__right_motor_speed = value
        self.__update_motors()

    @property
    def left_motor_speed(self):
        return self.__left_motor_speed

    @left_motor_speed.setter
    def left_motor_speed(self, value):
        self.__left_motor_speed = value
        self.__update_motors()

    @property
    def back_motor_speed(self):
        return self.__back_motor_speed

    @back_motor_speed.setter
    def back_motor_speed(self, value):
        self.__back_motor_speed = value
        self.__update_motors()

    @property
    def grip_servo_pos(self):
        return self.__grip_servo_pos

    @grip_servo_pos.setter
    def grip_servo_pos(self, value):
        self.__grip_servo_pos = value
        self.__update_oms()

    @property
    def reset_right_enc(self):
        return self.__reset_right_enc

    @reset_right_enc.setter
    def reset_right_enc(self, value):
        self.__reset_right_enc = value
        self.__update_resets()

    @property
    def reset_left_enc(self):
        return self.__reset_left_enc

    @reset_left_enc.setter
    def reset_left_enc(self, value):
        self.__reset_left_enc = value
        self.__update_resets()

    @property
    def reset_back_enc(self):
        return self.__reset_back_enc

    @reset_back_enc.setter
    def reset_back_enc(self, value):
        self.__reset_back_enc = value
        self.__update_resets()

    @property
    def reset_imu(self):
        return self.__reset_imu

    @reset_imu.setter
    def reset_imu(self, value):
        self.__reset_imu = value
        self.__update_resets()

    @property
    def right_motor_enc(self):
        self.__update_encs()
        return self.__right_motor_enc

    @property
    def left_motor_enc(self):
        self.__update_encs()
        return self.__left_motor_enc

    @property
    def back_motor_enc(self):
        self.__update_encs()
        return self.__back_motor_enc

    @property
    def ir_1(self):
        self.__update_sensors()
        return self.__ir_1

    @property
    def ir_2(self):
        self.__update_sensors()
        return self.__ir_2

    @property
    def ir_3(self):
        self.__update_sensors()
        return self.__ir_3

    @property
    def ir_4(self):
        self.__update_sensors()
        return self.__ir_4

    @property
    def ir_5(self):
        self.__update_sensors()
        return self.__ir_5

    @property
    def ir_6(self):
        self.__update_sensors()
        return self.__ir_6

    @property
    def ir_7(self):
        self.__update_sensors()
        return self.__ir_7

    @property
    def ir_8(self):
        self.__update_sensors()
        return self.__ir_8

    @property
    def ir_9(self):
        self.__update_sensors()
        return self.__ir_9

    @property
    def imu(self):
        self.__update_sensors()
        return self.__imu
