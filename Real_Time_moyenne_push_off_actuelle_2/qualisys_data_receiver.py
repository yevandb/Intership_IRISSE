import qtm_rt
import numpy as np
from qtm_rt.packet import QRTComponentType
import struct
import xml.etree.ElementTree as ET


async def connecter_qualisys(ip="127.0.0.1"):
    connection = await qtm_rt.connect(ip)
    if connection is None:
        raise ConnectionError("Échec de connexion à QTM.")
    print("Connecté à QTM.")
    return connection


async def get_emg_frame(connection, index_emg, index_grf):

    while True:
        packet = await connection.get_current_frame(components=["analog"])

        if QRTComponentType.ComponentAnalog not in packet.components:
            continue

        try:
            component, data_list = packet.get_analog()
        except struct.error:
            continue

        # result = await connection.get_parameters(parameters=["analog"])
        # labels_dict = extraire_labels_analog(result)
        """
        for dev_id, infos in labels_dict.items():
            print(f"Device ID: {dev_id}, Name: {infos['name']}")
            for i, label in enumerate(infos["labels"]):
                print(f"  Channel {i}: {label}")
        """

        emg_data = []
        grf_data = []

        for dev, _, chan in data_list:
            if dev.id == 2:
                emg_data.append(chan.samples)
            elif dev.id == 1:
                grf_data.append(chan.samples)

        if not emg_data or not grf_data:
            continue

        emg_data = np.array(emg_data, dtype=float)
        grf_data = np.array(grf_data, dtype=float)

        return emg_data[index_emg], grf_data[index_grf]


def extraire_labels_analog(result_bytes):
    xml_str = result_bytes.decode("utf-8")

    root = ET.fromstring(xml_str)

    devices = root.find("Analog").findall("Device")

    all_labels = {}
    for device in devices:
        device_id = int(device.find("Device_ID").text)
        device_name = device.find("Device_Name").text
        channels = device.findall("Channel")

        labels = [ch.find("Label").text for ch in channels]
        all_labels[device_id] = {"name": device_name, "labels": labels}

    return all_labels
