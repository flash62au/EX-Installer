"""
Module containing details for each product able to be installed with EX-Installer
"""

from . import images

product_details = {
    "ex_commandstation": {
        "product_name": "EX-CommandStation",
        "product_logo": images.EX_COMMANDSTATION_LOGO,
        "repo_name": "DCC-EX/CommandStation-EX",
        "repo_url": "https://github.com/DCC-EX/CommandStation-EX.git",
        "archive_url": "https://github.com/DCC-EX/CommandStation-EX/archive/refs/tags/",
        "supported_devices": [
            "arduino:avr:uno",
            "arduino:avr:nano",
            "arduino:avr:nano:cpu=atmega328",
            "arduino:avr:mega",
            "esp32:esp32:esp32",
            "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F411RE",
            "STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_F446RE"
        ]
    }
}