

class Channels:
    def __init__(self, controller, adcWrapper, adcWrapper1, debug=False):

        sensors = [
            {
                'pos': 1,
                'active': True,
                'controller': controller,
                'sensor': 'acs712',
                'pin': 27,
                'sensibility': 0.060,
                'min_amperes': 0.4
            },
            {
                'pos': 2,
                'active': True,
                'controller': controller,
                'sensor': 'acs712',
                'pin': 26,
                'sensibility': 0.0396,
                'min_amperes': 0.7
            },
            {
                'pos': 3,
                'active': True,
                'controller': adcWrapper,
                'sensor': 'acs712',
                'pin': 0,
                'sensibility': 0.100,
                'min_amperes': 0.15
            },
            {
                'pos': 4,
                'active': True,
                'controller': adcWrapper,
                'sensor': 'acs712',
                'pin': 1,
                'sensibility': 0.100,
                'min_amperes': 0.15
            },
            {
                'pos': 5,
                'active': True,
                'controller': adcWrapper,
                'sensor': 'acs712',
                'pin': 2,
                'sensibility': 0.100,
                'min_amperes': 0.15
            },
            {
                'pos': 6,
                'active': True,
                'controller': adcWrapper,
                'sensor': 'acs712',
                'pin': 3,
                'sensibility': 0.100,
                'min_amperes': 0.15
            },
            {
                'pos': 7,
                'active': True,
                'controller': adcWrapper1,
                'sensor': 'acs712',
                'pin': 0,
                'sensibility': 0.100,
                'min_amperes': 0.15
            },
            {
                'pos': 8,
                'active': True,
                'controller': adcWrapper1,
                'sensor': 'acs712',
                'pin': 1,
                'sensibility': 0.100,
                'min_amperes': 0.15
            },
            {
                'pos': 9,
                'active': True,
                'controller': adcWrapper1,
                'sensor': 'acs712',
                'pin': 2,
                'sensibility': 0.100,
                'min_amperes': 0.15
            },
            {
                'pos': 10,
                'active': True,
                'controller': adcWrapper1,
                'sensor': 'acs712',
                'pin': 3,
                'sensibility': 0.100,
                'min_amperes': 0.15
            },
        ]

        self.SENSORS = sensors

    def getSensors(self):
        return self.SENSORS
