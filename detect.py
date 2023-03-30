import time
import requests  # pip3 install requests
import sched
import json
import logging
import sys

# set up logging to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(message)s')
console_handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[console_handler])

# how ofter to check kismet for new devices
check_interval = 300  # seconds

# Details of your kismet server
kismet_ip = "your_kismet_ip"
kismet_port = "2501"
kismet_username = "your_kismet_username"
kismet_password = "your_kismet_password"

# Initialize the scheduler
scheduler = sched.scheduler(timefunc=time.time)


def cool_logo_in_log():
    logging.info("""
██████╗ ███████╗████████╗███████╗ ██████╗████████╗    █████╗       ██████╗ ██╗      ██████╗ ██████╗ 
██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝   ██╔══██╗      ██╔══██╗██║     ██╔═══██╗██╔══██╗
██║  ██║█████╗     ██║   █████╗  ██║        ██║█████╗███████║█████╗██████╔╝██║     ██║   ██║██║  ██║
██║  ██║██╔══╝     ██║   ██╔══╝  ██║        ██║╚════╝██╔══██║╚════╝██╔═══╝ ██║     ██║   ██║██║  ██║
██████╔╝███████╗   ██║   ███████╗╚██████╗   ██║      ██║  ██║      ██║     ███████╗╚██████╔╝██████╔╝
╚═════╝ ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝   ╚═╝      ╚═╝  ╚═╝      ╚═╝     ╚══════╝ ╚═════╝ ╚═════╝                                                                                           
""")
    logging.info(f"Starting Plod Watcher, checking every {check_interval} seconds")

def found_plod_in_log():
    logging.info("""
 █████╗ ██╗     ███████╗██████╗ ████████╗
██╔══██╗██║     ██╔════╝██╔══██╗╚══██╔══╝
███████║██║     █████╗  ██████╔╝   ██║   
██╔══██║██║     ██╔══╝  ██╔══██╗   ██║   
██║  ██║███████╗███████╗██║  ██║   ██║   
╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   
""")

def fetch_and_check_kismet_data():
    # fetch data from kismet endpoint
    kismet_endpoint = f"http://{kismet_username}:{kismet_password}@{kismet_ip}:{kismet_port}/devices/last-time/{-check_interval}/devices.json"
    logging.info(f"Fetching data from {kismet_endpoint}")

    try:
        response = requests.get(kismet_endpoint)
        data = json.loads(response.text)
    except Exception as e:
        logging.error(f"Error fetching data from kismet: {e}")
        return

    for device in data:
        print(device)
        # check if device is has axon MAC address, common bodycam manufacturer
        if device['kismet.device.base.macaddr'].startswith("00:25:DF") or \
                device['kismet.device.base.macaddr'].startswith("12:20:13") or \
                device['kismet.device.base.commonname'].startswith("Axon"):
            found_plod_in_log()
            message_text = f'Police axon device detected: {device["kismet.device.base.macaddr"]} {device["kismet.device.base.commonname"]} {device["kismet.device.base.name"]}'
            logging.info(message_text)

        # Check if a sierra wireless airlink router is seen, used in police cars in some areas
        if device['kismet.device.base.macaddr'].startswith("00:14:3E"):
            found_plod_in_log()
            message_text = f'In car sierra wireless airlink router detected: {device["kismet.device.base.macaddr"]} {device["kismet.device.base.commonname"]} {device["kismet.device.base.name"]}'
            logging.info(message_text)


def run_scheduler():
    # Schedule the function to run after check_interval seconds
    scheduler.enter(check_interval, 1, run_scheduler)
    fetch_and_check_kismet_data()


if __name__ == "__main__":
    cool_logo_in_log()

    scheduler.enter(check_interval, 1, run_scheduler)
    scheduler.run()
