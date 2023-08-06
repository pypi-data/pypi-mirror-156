from pymavlink import mavutil

mode = ""


class DoReposition:
    def __init__(self, connection_object):
        self.connection_object = connection_object

    def go_waypoint(self, lat, lon, alt):
        self.connection_object.mav.command_int_send(
            0,
            0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            mavutil.mavlink.MAV_CMD_DO_REPOSITION,
            0,
            0,
            -1,
            0,
            0,
            0,
            int(lat * 1e7),
            int(lon * 1e7),
            alt,
        )
        m = self.connection_object.recv_match(type='COMMAND_ACK',
                                              blocking=True,
                                              timeout=0.1)
