class NotInVoiceChannelException(Exception):
    def __init__(self):
        self.msg = "User must be in voice channel to play music"
