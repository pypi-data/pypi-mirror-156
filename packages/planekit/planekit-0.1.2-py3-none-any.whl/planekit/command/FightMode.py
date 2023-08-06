import sys
from planekit.mavlink.SendMessage import SendMessage
from planekit.mavlink.ReceiveData import ReceiveData

mode = ""


class FlightMode:
    def __init__(self, connection_object):
        self.connection_object = connection_object
        self.arm_status = None

    def set_flight_mode(self, mode):
        # Choose a mode
        send_message = SendMessage(self.connection_object)

        if mode not in self.connection_object.mode_mapping():
            print('Unknown mode : {}'.format(mode))
            print('Try:', list(self.connection_object.mode_mapping().keys()))
            sys.exit(1)

        # Get mode ID
        mode_id = self.connection_object.mode_mapping()[mode]
        # Set new mode
        # self.connection_object.mav.command_long_send(
        #    self.connection_object.target_system, self.connection_object.target_component,
        #    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        #    0, mode_id, 0, 0, 0, 0, 0) or:
        # self.connection_object.set_mode(mode_id) or:
        self.connection_object.mav.set_mode_send(
            self.connection_object.target_system,
            send_message.mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id)
        # Wait for ACK command
        # Would be good to add mechanism to avoid endlessly blocking
        # if the autopilot sends a NACK or never receives the message
        ack_msg = self.connection_object.recv_match(type='COMMAND_ACK', blocking=True)
        ack_msg = ack_msg.to_dict()

    def get_flight_mode(self):
        global mode
        all_mode = ['MANUAL', 'CIRCLE', 'STABILIZE', 'TRAINING', 'ACRO', 'FBWA', 'FBWB', 'CRUISE', 'AUTOTUNE', "",
                    'AUTO',
                    'RTL', 'LOITER', 'TAKEOFF', 'AVOID_ADSB', 'GUIDED', 'INITIALISING', 'QSTABILIZE', 'QHOVER',
                    'QLOITER', 'QLAND', 'QRTL', 'QAUTOTUNE', 'QACRO', 'THERMAL', 'LOITERALTQLAND']

        receive_data = ReceiveData(self.connection_object)
        heartbeat = receive_data.select_heartbeat_message().get_all_state()
        if heartbeat.type == 1:
            mode = all_mode[heartbeat.custom_mode]
        return mode
