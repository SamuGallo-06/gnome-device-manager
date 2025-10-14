import gi
import re
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from translationsProxy import tr
from devices import USB_Device, PCI_Device, Display, Network_Device, Input_Device

class GnomeDeviceManager(Gtk.Window):
    def __init__(self):
        super().__init__(title=tr.title)
        self.set_default_size(600, 400)
        self.SetupUi()
        self.RefreshDeviceList()

    def SetupUi(self):
        headerBar = Gtk.HeaderBar()
        headerBar.set_show_close_button(True)
        headerBar.props.title = tr.title
        self.set_titlebar(headerBar)

        # menu hamburger
        menuButton = Gtk.MenuButton()
        icon = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
        menuButton.add(icon)
        headerBar.pack_end(menuButton)

        popover = Gtk.Popover()
        menuBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        popover.add(menuBox)

        btnRefresh = Gtk.ModelButton(label=tr.refresh_list)
        btnRefresh.connect("clicked", self.RefreshDeviceList)
        btnQuit = Gtk.ModelButton(label=tr.exit_text)
        btnQuit.connect("clicked", Gtk.main_quit)
        menuBox.pack_start(btnRefresh, True, True, 0)
        menuBox.pack_start(btnQuit, True, True, 0)

        popover.show_all()
        popover.hide()
        menuButton.set_popover(popover)

        # TreeView
        self.deviceTreeStore = Gtk.TreeStore(str, str, object)
        self.treeView = Gtk.TreeView(model=self.deviceTreeStore)
        renderer = Gtk.CellRendererText()
        self.treeView.append_column(Gtk.TreeViewColumn(tr.device_name_text, renderer, text=0))
        self.treeView.append_column(Gtk.TreeViewColumn(tr.device_type_text, renderer, text=1))
        self.treeView.connect("button-press-event", self.OnRightClick)

        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.treeView)
        self.add(scrolled)

    def OnRightClick(self, treeView, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            pathInfo = treeView.get_path_at_pos(int(event.x), int(event.y))
            if pathInfo:
                path, col, _, _ = pathInfo
                treeView.grab_focus()
                treeView.set_cursor(path, col, 0)

                menu = Gtk.Menu()

                propItem = Gtk.MenuItem(label=tr.properties_text)
                propItem.connect("activate", self.OnProperties, path)
                menu.append(propItem)

                disableItem = Gtk.MenuItem(label=tr.disable_device_text)
                disableItem.connect("activate", self.OnDisable, path)
                menu.append(disableItem)

                disconnectItem = Gtk.MenuItem(label=tr.disconnect_device_text)
                disconnectItem.connect("activate", self.OnDisconnect, path)
                menu.append(disconnectItem)

                menu.show_all()
                menu.popup_at_pointer(event)
            return True
    
    def OnDisable(self, widget, path):
        model = self.treeView.get_model()
        device = model[path][2]
        if not device:
            return

        dialog = Gtk.MessageDialog(
            self, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO,
            f"{tr.disable_device_text} {device.name}?"
        )
        dialog.format_secondary_text(tr.disable_device_desc)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            success = self.DisableDevice(device)
            msg = tr.device_disabled if success else tr.disable_failed
            self.ShowInfo(msg)
            
    def OnDisconnect(self, widget, path):
        model = self.treeView.get_model()
        device = model[path][2]
        if not device:
            return

        dialog = Gtk.MessageDialog(
            self, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO,
            f"{tr.disconnect_device_text} {device.name}?"
        )
        dialog.format_secondary_text(tr.disconnect_device_desc)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            success = self.DisconnectDevice(device)
            msg = tr.device_disconnected if success else tr.disconnect_failed
            self.ShowInfo(msg)
        
    def DisableDevice(self, device):
        try:
            if device.device_type == "Network Device":
                cmd = f"nmcli device disconnect {device.name}"
            elif device.device_type == "Input Device":
                cmd = f"xinput disable '{device.name}'"
            elif device.device_type == "Display":
                cmd = f"xrandr --output {device.name} --off"
            elif device.device_type == "USB Device":
                cmd = f"echo 0 > /sys/bus/usb/devices/{device.bus}-{device.device_number}/authorized"
            else:
                return False

            subprocess.run([
                "pkexec", "bash", "-c",
                f'echo "{tr.auth_message}" && {cmd}'
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def ShowInfo(self, message):
        dialog = Gtk.MessageDialog(
            self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, message
        )
        dialog.run()
        dialog.destroy()

    def OnProperties(self, widget, path):
        model = self.treeView.get_model()
        device = model[path][2]
        if not device:
            return

        props = device.get_properties()
        prop_text = "\n".join(f"{k}: {v}" for k, v in props.items())

        dialog = Gtk.MessageDialog(
            self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
            f"{tr.properties_text} - {device.name}"
        )
        dialog.format_secondary_text(prop_text)
        dialog.run()
        dialog.destroy()

    def RefreshDeviceList(self, widget=None):
        self.deviceTreeStore.clear()

        # USB
        usb_iter = self.deviceTreeStore.append(None, ["USB Devices", "", None])
        lsusb = subprocess.getoutput("lsusb")
        for line in lsusb.splitlines():
            m = re.match(r"Bus (\d+) Device (\d+): ID ([0-9a-f]{4}):([0-9a-f]{4}) (.+)", line)
            if m:
                dev = USB_Device(*m.groups())
                self.deviceTreeStore.append(usb_iter, [dev.name, dev.device_type, dev])

        # PCI
        pci_iter = self.deviceTreeStore.append(None, ["PCI Devices", "", None])
        lspci = subprocess.getoutput("lspci")
        for line in lspci.splitlines():
            dev = PCI_Device(line.strip())
            self.deviceTreeStore.append(pci_iter, [dev.name, dev.device_type, dev])

        # Displays
        disp_iter = self.deviceTreeStore.append(None, ["Displays", "", None])
        xrandr = subprocess.getoutput("xrandr --query")
        for line in xrandr.splitlines():
            if " connected" in line:
                name = line.split()[0]
                res = "Unknown"
                if "+" in line:
                    parts = line.split()
                    if len(parts) > 2:
                        res = parts[2]
                dev = Display(name, res)
                self.deviceTreeStore.append(disp_iter, [dev.name, dev.device_type, dev])

        # Network
        net_iter = self.deviceTreeStore.append(None, ["Network Devices", "", None])
        ip_out = subprocess.getoutput("ip link")
        for line in ip_out.splitlines():
            m = re.match(r"\d+: (\S+):", line)
            if m:
                dev = Network_Device(m.group(1))
                self.deviceTreeStore.append(net_iter, [dev.name, dev.device_type, dev])

        # Input
        inp_iter = self.deviceTreeStore.append(None, ["Input Devices", "", None])
        xinput = subprocess.getoutput("xinput list")
        for line in xinput.splitlines():
            m = re.search(r'↳ (.+?)\s+id=\d+', line)
            if m:
                dev = Input_Device(m.group(1))
                self.deviceTreeStore.append(inp_iter, [dev.name, dev.device_type, dev])
                
    def DisconnectDevice():
        print("DisconnectDevice not implemented")
        


if __name__ == "__main__":
    app = GnomeDeviceManager()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()