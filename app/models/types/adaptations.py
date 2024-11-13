from enum import Enum


class Adaptations(str, Enum):
    """Based on the CHS adaptation details list"""

    BSL_WEBCAM = "BSL - Webcam"
    MINICOM = "Minicom"
    TXT_RELAY = "Text Relay"
    SKYPE = "Skype"
    CALLBACK_PREFERENCE = "Callback Preference"
