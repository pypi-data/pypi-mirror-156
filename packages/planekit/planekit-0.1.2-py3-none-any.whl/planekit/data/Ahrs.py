class Ahrs:
    def __init__(self, ahrs_message):
        self.ahrs_message = ahrs_message

    def get_all_messages(self):
        return self.ahrs_message
