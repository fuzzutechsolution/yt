import customtkinter as ctk
from tkinter import messagebox
import socket
import threading
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


CAMERA_PORTS = {
    80: "HTTP",
    443: "HTTPS",
    554: "RTSP",
    8000: "CAM",
    8080: "WEB",
    8554: "RTSP",
    37777: "DVR",
    34567: "NVR",
}


def get_local_ip():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        sock.connect(("8.8.8.8", 80))

        return sock.getsockname()[0]

    except:

        return "192.168.1.1"

    finally:

        sock.close()


def get_network():

    ip = get_local_ip()

    return str(

        ipaddress.ip_network(

            f"{ip}/24",

            strict=False

        )

    )


def check_port(ip, port):

    sock = socket.socket(

        socket.AF_INET,

        socket.SOCK_STREAM

    )

    sock.settimeout(.20)

    try:

        return sock.connect_ex(

            (ip, port)

        ) == 0

    except:

        return False

    finally:

        sock.close()


def scan_ports(ip):

    open_ports = []

    with ThreadPoolExecutor(
        max_workers=8
    ) as executor:

        futures = {

            executor.submit(
                check_port,
                ip,
                port
            ): port

            for port in CAMERA_PORTS

        }

        for future in as_completed(futures):

            port = futures[future]

            if future.result():

                open_ports.append(port)

    return sorted(open_ports)


def ping_device(ip):

    try:

        socket.gethostbyaddr(ip)

        return True

    except:

        # Port probes provide a lightweight fallback.
        return any(

            check_port(ip, port)

            for port in [80, 443, 554, 8080]

        )


def discover_devices(network):

    net = ipaddress.ip_network(

        network,

        strict=False

    )

    hosts = list(net.hosts())

    devices = []

    with ThreadPoolExecutor(
        max_workers=50
    ) as executor:

        futures = {

            executor.submit(
                ping_device,
                str(ip)
            ): str(ip)

            for ip in hosts

        }

        for future in as_completed(futures):

            if future.result():

                devices.append(

                    futures[future]

                )

    return devices


def risk_score(ports):

    score = 0

    if 554 in ports:

        score += 55

    if 8554 in ports:

        score += 45

    if 37777 in ports:

        score += 40

    if 34567 in ports:

        score += 40

    if 8000 in ports:

        score += 20

    if 80 in ports or 8080 in ports:

        score += 10

    return min(score, 100)


class CameraDetector(ctk.CTk):

    def __init__(self):

        super().__init__()

        # STRICT PORTRAIT GUI

        self.title(
            "FuzzuTech | Hidden Camera Detector"
        )

        self.geometry("540x960")

        self.minsize(540, 960)

        self.maxsize(540, 960)

        self.resizable(False, False)

        self.configure(
            fg_color="#07100D"
        )

        self.scanning = False

        self.build_gui()


    def build_gui(self):

        # HEADER

        header = ctk.CTkFrame(

            self,

            height=150,

            corner_radius=0,

            fg_color="#091713"

        )

        header.pack(

            fill="x"

        )

        ctk.CTkLabel(

            header,

            text="◉  F U Z Z U T E C H",

            text_color="#32E6A1",

            font=ctk.CTkFont(

                size=14,

                weight="bold"

            )

        ).pack(

            pady=(22, 7)

        )

        ctk.CTkLabel(

            header,

            text="HIDDEN CAMERA\nDETECTOR",

            font=ctk.CTkFont(

                size=31,

                weight="bold"

            ),

            justify="center"

        ).pack()

        ctk.CTkLabel(

            header,

            text="AI NETWORK SECURITY SCANNER",

            text_color="#7B8F88",

            font=ctk.CTkFont(

                size=11

            )

        ).pack(

            pady=6

        )


        # MAIN PANEL

        panel = ctk.CTkFrame(

            self,

            corner_radius=20,

            fg_color="#101B17"

        )

        panel.pack(

            fill="x",

            padx=20,

            pady=18

        )


        ctk.CTkLabel(

            panel,

            text="NETWORK RANGE",

            font=ctk.CTkFont(

                size=12,

                weight="bold"

            ),

            anchor="w"

        ).pack(

            fill="x",

            padx=18,

            pady=(17, 5)

        )


        self.network_entry = ctk.CTkEntry(

            panel,

            height=44,

            corner_radius=10,

            border_color="#1E5A45",

            fg_color="#09120F"

        )

        self.network_entry.pack(

            fill="x",

            padx=18

        )

        self.network_entry.insert(

            0,

            get_network()

        )


        self.scan_button = ctk.CTkButton(

            panel,

            text="START SECURITY SCAN",

            height=50,

            corner_radius=12,

            font=ctk.CTkFont(

                size=15,

                weight="bold"

            ),

            command=self.start_scan

        )

        self.scan_button.pack(

            fill="x",

            padx=18,

            pady=16

        )


        # STATUS

        self.status_title = ctk.CTkLabel(

            self,

            text="SYSTEM READY",

            text_color="#32E6A1",

            font=ctk.CTkFont(

                size=18,

                weight="bold"

            )

        )

        self.status_title.pack(

            pady=(2, 8)

        )


        # RESULTS CONTAINER

        self.results = ctk.CTkScrollableFrame(

            self,

            height=410,

            corner_radius=18,

            fg_color="#0D1714",

            label_text="DISCOVERED DEVICES",

            label_font=ctk.CTkFont(

                size=13,

                weight="bold"

            )

        )

        self.results.pack(

            fill="both",

            expand=True,

            padx=20,

            pady=(0, 15)

        )


        # BOTTOM STATUS

        footer = ctk.CTkFrame(

            self,

            height=90,

            corner_radius=0,

            fg_color="#09130F"

        )

        footer.pack(

            fill="x",

            side="bottom"

        )


        self.progress = ctk.CTkProgressBar(

            footer,

            height=8,

            progress_color="#32E6A1"

        )

        self.progress.pack(

            fill="x",

            padx=20,

            pady=(17, 8)

        )

        self.progress.set(0)


        self.status = ctk.CTkLabel(

            footer,

            text="SECURITY SYSTEM ONLINE",

            text_color="#71827C",

            font=ctk.CTkFont(

                size=11

            )

        )

        self.status.pack()


    def clear_results(self):

        for widget in self.results.winfo_children():

            widget.destroy()


    def create_device_card(

        self,

        ip,

        ports,

        score

    ):

        if score >= 70:

            status = "HIGH RISK"

            status_color = "#FF3D5A"

        elif score >= 30:

            status = "SUSPICIOUS"

            status_color = "#FFB020"

        else:

            status = "SAFE"

            status_color = "#32E6A1"


        card = ctk.CTkFrame(

            self.results,

            height=125,

            corner_radius=14,

            fg_color="#14231E",

            border_width=1,

            border_color=status_color

        )

        card.pack(

            fill="x",

            padx=5,

            pady=7

        )


        top = ctk.CTkFrame(

            card,

            fg_color="transparent"

        )

        top.pack(

            fill="x",

            padx=15,

            pady=(13, 4)

        )


        ctk.CTkLabel(

            top,

            text="DEVICE",

            text_color="#71827C",

            font=ctk.CTkFont(

                size=10,

                weight="bold"

            )

        ).pack(

            side="left"

        )


        ctk.CTkLabel(

            top,

            text=status,

            text_color=status_color,

            font=ctk.CTkFont(

                size=11,

                weight="bold"

            )

        ).pack(

            side="right"

        )


        ctk.CTkLabel(

            card,

            text=ip,

            anchor="w",

            font=ctk.CTkFont(

                size=20,

                weight="bold"

            )

        ).pack(

            fill="x",

            padx=15

        )


        port_text = (

            "OPEN PORTS  " +

            ", ".join(

                map(str, ports)

            )

            if ports

            else

            "OPEN PORTS  NONE"

        )


        ctk.CTkLabel(

            card,

            text=port_text,

            anchor="w",

            text_color="#8A9C95",

            font=ctk.CTkFont(

                size=11

            )

        ).pack(

            fill="x",

            padx=15,

            pady=(5, 2)

        )


        ctk.CTkLabel(

            card,

            text=f"CAMERA RISK SCORE   {score}%",

            anchor="w",

            text_color=status_color,

            font=ctk.CTkFont(

                size=12,

                weight="bold"

            )

        ).pack(

            fill="x",

            padx=15,

            pady=(2, 12)

        )


    def start_scan(self):

        if self.scanning:

            return


        try:

            network = self.network_entry.get()

            ipaddress.ip_network(

                network,

                strict=False

            )

        except:

            messagebox.showerror(

                "Network Error",

                "Invalid Network Range"

            )

            return


        self.scanning = True

        self.clear_results()

        self.progress.set(0)

        self.status_title.configure(

            text="SCANNING NETWORK..."

        )

        self.scan_button.configure(

            state="disabled",

            text="SCANNING..."

        )


        threading.Thread(

            target=self.scan,

            args=(network,),

            daemon=True

        ).start()


    def scan(self, network):

        try:

            devices = discover_devices(

                network

            )


            total = len(devices)


            if total == 0:

                self.after(

                    0,

                    lambda:

                    self.status_title.configure(

                        text="NO DEVICES DETECTED"

                    )

                )

                return


            threats = 0


            for index, ip in enumerate(

                devices,

                start=1

            ):

                self.after(

                    0,

                    lambda i=ip:

                    self.status.configure(

                        text=f"ANALYZING {i}"

                    )

                )


                ports = scan_ports(ip)

                score = risk_score(ports)


                if score >= 30:

                    threats += 1


                self.after(

                    0,

                    lambda i=ip,

                    p=ports,

                    s=score:

                    self.create_device_card(

                        i,

                        p,

                        s

                    )

                )


                progress = (

                    index / total

                )


                self.after(

                    0,

                    lambda value=progress:

                    self.progress.set(

                        value

                    )

                )


            final_text = (

                f"{total} DEVICES • "

                f"{threats} THREATS DETECTED"

            )


            self.after(

                0,

                lambda:

                self.status_title.configure(

                    text=final_text

                )

            )


            if threats:

                self.after(

                    0,

                    lambda:

                    messagebox.showwarning(

                        "SECURITY ALERT",

                        "POTENTIAL CAMERA DEVICE DETECTED!"

                    )

                )


            self.after(

                0,

                lambda:

                self.status.configure(

                    text="SECURITY SCAN COMPLETE"

                )

            )


        except Exception as error:

            self.after(

                0,

                lambda e=str(error):

                messagebox.showerror(

                    "ERROR",

                    e

                )

            )


        finally:

            self.scanning = False


            self.after(

                0,

                lambda:

                self.scan_button.configure(

                    state="normal",

                    text="SCAN AGAIN"

                )

            )


if __name__ == "__main__":

    app = CameraDetector()

    app.mainloop()