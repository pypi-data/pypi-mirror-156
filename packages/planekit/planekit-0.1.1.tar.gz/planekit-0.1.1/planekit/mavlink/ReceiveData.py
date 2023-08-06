from planekit.data.Gps import Gps
from planekit.data.Heartbeat import Heartbeat
from planekit.data.Imu import Imu
from planekit.data.Ahrs import Ahrs


class ReceiveData:
    """
    En:
        This class parses mavtcp messages by type and sends them to the corresponding classes.
        :arg connection_object
            Gets the object instance pymavlink.mavutil.mavtcp
    Tr:
        Bu sınıf, mavtcp mesajlarını get_type ile ayrıştırır ve bunları ilgili sınıflara gönderir.
        :arg connection_object
            pymavlink.mavutil.mavtcp den türetilmiş objeyi alır
    """

    def __init__(self, connection_object):
        self.connection_object = connection_object
        self.message_object = None
        self.imu_message = None
        self.gps_message = None
        self.heartbeat_message = None
        self.ahrs_message = None

    def get_message_object(self):
        """
        en:
            :return:
            self.message_object : Return messages received with recv_match.
        tr:
            :return:
                self.message_object : recv_match ile alınan mesajları dönderir.
        """

        self.message_object = self.connection_object.recv_match()
        return self.message_object

    def select_imu_message(self):
        """
        En:
            This func. selects imu messages received from self.get_message_object.
        Tr:
            Bu func. self.get_message_object'den alınan imu mesajlarını seçer.
        """

        while True:
            self.imu_message = self.get_message_object()
            if self.imu_message is not None and self.imu_message.get_type() == 'RAW_IMU':
                imu_message = Imu(self.imu_message)
                return imu_message

    def select_gps_message(self):
        """
            En:
                This func. selects gps messages received from self.get_message_object.
            Tr:
                Bu func. self.get_message_object'den alınan gps mesajlarını seçer.
        """

        while True:
            self.gps_message = self.get_message_object()
            if self.gps_message is not None and self.gps_message.get_type() == 'GPS_RAW_INT':
                gps_message = Gps(self.gps_message)
                return gps_message

    def select_heartbeat_message(self):
        """
        En: This func. if heartbeat_message.get_type() equals 'HEARTBEAT', selects received message from
        self.get_message_object. Tr: Bu func. self.get_message_object'den alınan heartbeat mesajlarını seçer.
        """

        while True:
            self.heartbeat_message = self.get_message_object()
            if self.heartbeat_message is not None and self.heartbeat_message.get_type() == 'HEARTBEAT':
                heartbeat_message = Heartbeat(self.heartbeat_message)
                return heartbeat_message

    def select_ahrs_message(self):
        while True:
            self.ahrs_message = self.get_message_object()
            if self.ahrs_message is not None and self.ahrs_message.get_type() == 'AHRS2':
                ahrs_message = Ahrs(self.ahrs_message)
                return ahrs_message


    """
    def arm_status(self):
            En:
                Heartbeat(self.heartbeat_message).arm can have 3 values.
                These are True(if arm) False(if disarm) and -1(another thing).
            Tr:
                Heartbeat(self.heartbeat_message).arm 3 değere sahip olabilir.
                Bunlar True(if arm) False(if disarm) ve -1(another thing) olabilir.

        while True:
            self.heartbeat_message = planekit.ReceiveData(self.connection_object).get_message_object()
            if self.heartbeat_message is not None and self.heartbeat_message.get_type() == 'HEARTBEAT':
                heartbeat_message = Heartbeat(self.heartbeat_message)
                if heartbeat_message.is_arm() != -1:
                    return heartbeat_message.is_arm()
    """

    def arm_status(self):
        if self.connection_object.motors_armed() == 128:
            return True
        if self.connection_object.motors_armed() == 0:
            return False

    def ground_speed_message(self):
        """
            En:
                :return:
                    Return the vel parameter from messages with type GPS_RAW_INT
            Tr:
                :return:
                    GPS_RAW_INT tipine sahip mesajlardan vel parametresini dönderir
        """

        while True:
            self.gps_message = self.get_message_object()
            if self.gps_message is not None and self.gps_message.get_type() == 'GPS_RAW_INT':
                gps_message = Gps(self.gps_message)
                return gps_message.vel

    def alt(self, relative=True, timeout=30):
        """returns vehicles altitude in metres, possibly relative-to-home"""
        msg = self.connection_object.recv_match(type='GLOBAL_POSITION_INT',
                                                blocking=True,
                                                timeout=timeout)
        return msg.relative_alt / 1000
