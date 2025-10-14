import re
import subprocess

class BaseDevice:
    """Classe base per tutti i dispositivi: definisce interfaccia e metodi comuni."""
    def __init__(self, name, device_type):
        self.name = name
        self.device_type = device_type
        self.vendor = "Unknown"
        self.model = "Unknown"
        self.driver = "Unknown"
        self.status = "Active"

    def get_properties(self):
        """Restituisce un dizionario con le proprietà principali del device."""
        return {
            "Name": self.name,
            "Type": self.device_type,
            "Vendor": self.vendor,
            "Model": self.model,
            "Driver": self.driver,
            "Status": self.status
        }

    def __str__(self):
        return f"{self.device_type}: {self.name}"


# ------------------- USB -------------------
class USB_Device(BaseDevice):
    def __init__(self, bus, device, vendor_id, product_id, name):
        super().__init__(name, "USB Device")
        self.bus = bus
        self.device_number = device
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.identifier = f"{vendor_id}:{product_id}"

        # Recupera produttore e modello da lsusb
        try:
            info = subprocess.check_output(["lsusb", "-d", self.identifier], text=True)
            match_vendor = re.search(r"ID\s+[0-9a-f]{4}:[0-9a-f]{4}\s+(.+)", info)
            if match_vendor:
                self.vendor = match_vendor.group(1).split()[0]
                self.model = " ".join(match_vendor.group(1).split()[1:])
        except Exception:
            pass

    def get_properties(self):
        props = super().get_properties()
        props.update({
            "Bus": self.bus,
            "Device Number": self.device_number,
            "Vendor ID": self.vendor_id,
            "Product ID": self.product_id
        })
        return props


# ------------------- PCI -------------------
class PCI_Device(BaseDevice):
    def __init__(self, device_info):
        super().__init__(device_info, "PCI Device")
        self.device_info = device_info
        self.device_bdf = device_info.split()[0] if device_info else "Unknown"
        self.class_type = "Unknown"

        match = re.search(r"^\S+\s+(.+?):", device_info)
        if match:
            self.class_type = match.group(1).strip()

        # Prova a trovare il driver PCI associato
        try:
            lspci_v = subprocess.check_output(["lspci", "-vmmk"], text=True)
            section = re.findall(rf"Slot:\s+{re.escape(self.device_bdf)}\n(.*?)(?:\n\n|$)", lspci_v, re.S)
            if section:
                for line in section[0].splitlines():
                    if line.startswith("Vendor:"):
                        self.vendor = line.split(":", 1)[1].strip()
                    elif line.startswith("Device:"):
                        self.model = line.split(":", 1)[1].strip()
                    elif line.startswith("Driver:"):
                        self.driver = line.split(":", 1)[1].strip()
        except Exception:
            pass

    def get_properties(self):
        props = super().get_properties()
        props.update({
            "BDF": self.device_bdf,
            "Class Type": self.class_type
        })
        return props


# ------------------- Display -------------------
class Display(BaseDevice):
    def __init__(self, name, resolution):
        super().__init__(name, "Display")
        self.resolution = resolution
        self.refresh_rate = "Unknown"
        self.connected = True

        # Prova a estrarre refresh rate da xrandr
        try:
            xrandr_out = subprocess.check_output(["xrandr", "--verbose"], text=True)
            match = re.search(rf"{re.escape(name)} connected.*?(\d+\.\d+)\*", xrandr_out)
            if match:
                self.refresh_rate = match.group(1) + " Hz"
        except Exception:
            pass

    def get_properties(self):
        props = super().get_properties()
        props.update({
            "Resolution": self.resolution,
            "Refresh Rate": self.refresh_rate,
            "Connected": "Yes" if self.connected else "No"
        })
        return props


# ------------------- Network -------------------
class Network_Device(BaseDevice):
    def __init__(self, name):
        super().__init__(name, "Network Device")
        self.mac_address = "Unknown"
        self.state = "Unknown"
        self.driver = "Unknown"

        try:
            info = subprocess.check_output(["ip", "link", "show", name], text=True)
            if "state UP" in info:
                self.state = "Up"
            elif "state DOWN" in info:
                self.state = "Down"

            mac_match = re.search(r"link/\w+\s+([0-9a-f:]+)", info)
            if mac_match:
                self.mac_address = mac_match.group(1)
        except Exception:
            pass

    def get_properties(self):
        props = super().get_properties()
        props.update({
            "MAC Address": self.mac_address,
            "State": self.state
        })
        return props


# ------------------- Input -------------------
class Input_Device(BaseDevice):
    def __init__(self, name):
        super().__init__(name, "Input Device")
        self.input_type = "Unknown"
        self.enabled = True

        # Tenta di capire tipo da nome
        if "keyboard" in name.lower():
            self.input_type = "Keyboard"
        elif "mouse" in name.lower():
            self.input_type = "Mouse"
        elif "touchpad" in name.lower():
            self.input_type = "Touchpad"
        elif "touchscreen" in name.lower():
            self.input_type = "Touchscreen"

    def get_properties(self):
        props = super().get_properties()
        props.update({
            "Input Type": self.input_type,
            "Enabled": "Yes" if self.enabled else "No"
        })
        return props