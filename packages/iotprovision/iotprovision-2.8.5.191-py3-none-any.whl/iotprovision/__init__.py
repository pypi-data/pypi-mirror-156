"""
Python provisioning of IoT kits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

iotprovision is a command-line utility for provisioning Microchip AVR-IoT,
PIC-IoT and SAM-IoT kits for use with various cloud providers.

It is used as a CLI.

Type iotprovision --help to get help.

Overview
~~~~~~~~

iotprovision is available:
    * install using pip from pypi: https://pypi.org/project/iotprovision
    * browse source code on github: https://github.com/microchip-pic-avr-tools/iotprovision
    * read API documentation on github: https://microchip-pic-avr-tools.github.io/iotprovision
    * read the changelog on github: https://github.com/microchip-pic-avr-tools/iotprovision/blob/main/CHANGELOG.md

Dependencies
~~~~~~~~~~~~
iotprovision depends on pytrustplatform, pyawsutils and pyazureutils.
iotprovision depends on pykitcommander to manage Microchip IoT kit firmware
and connection.
iotprovision depends on pyedbglib for its transport protocol.
pyedbglib requires a USB transport library like libusb.
See pyedbglib package for more information: https://pypi.org/project/pyedbglib/
"""

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
