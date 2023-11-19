try:
    import subprocess
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import ttk
    import requests
    import json
except ImportError as e:
    print(f"Failed to import a required library: {e}")
    print("Installing required libraries...")
    
    try:
        subprocess.run(["pip", "install", "subprocess"])
        subprocess.run(["pip", "install", "tkinter"])
        subprocess.run(["pip", "install", "requests"])
        subprocess.run(["pip", "install", "json"])
        
        import subprocess
        import tkinter as tk
        from tkinter import filedialog
        from tkinter import ttk
        import requests
        import json
    except Exception as install_error:
        print(f"Failed to install required libraries: {install_error}")
        exit("Exiting...")

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FileFrens GUI")

        # Initialize alias dictionary
        self.alias = {}

        # Radio buttons to select sending or receiving
        self.mode_var = tk.StringVar()
        self.mode_var.set("sending")  # Set default to "Sending"
        
        self.mode_frame = tk.Frame(root)
        self.sending_radio = tk.Radiobutton(self.mode_frame, text="Sending", variable=self.mode_var, value="sending", command=self.toggle_buttons)
        self.sending_radio.grid(row=0, column=0, padx=5)
        self.receiving_radio = tk.Radiobutton(self.mode_frame, text="Receiving", variable=self.mode_var, value="receiving", command=self.toggle_buttons)
        self.receiving_radio.grid(row=0, column=1, padx=5)
        self.mode_frame.grid(row=0, column=0, pady=10, columnspan=2)

        # Entry widget for IP address
        self.ip_frame = tk.Frame(root)
        self.ip_label = tk.Label(self.ip_frame, text="Enter IP:")
        self.ip_label.grid(row=1, column=0, padx=5)
        self.ip_entry = tk.Entry(self.ip_frame)
        self.ip_entry.grid(row=1, column=1, padx=5)
        self.ip_frame.grid(row=1, column=0, pady=5, columnspan=2)

        # Dropdown menu for alias selection
        self.alias_frame = tk.Frame(root)
        self.alias_label = tk.Label(self.alias_frame, text="Select Alias:")
        self.alias_label.grid(row=2, column=0, padx=5)
        self.alias_var = tk.StringVar()
        self.alias_dropdown = ttk.Combobox(self.alias_frame, textvariable=self.alias_var)
        self.alias_dropdown.grid(row=2, column=1, padx=5)
        self.alias_dropdown.bind("<<ComboboxSelected>>", self.update_ip_entry)
        self.alias_frame.grid(row=2, column=0, pady=10, columnspan=2)

        # File selection button
        self.file_btn = tk.Button(root, text="Select File", command=self.select_file)
        self.file_btn.grid(row=3, column=0, padx=5, pady=10)

        # Destination selection button
        self.dest_btn = tk.Button(root, text="Select Destination", command=self.select_destination, state=tk.DISABLED)
        self.dest_btn.grid(row=3, column=1, padx=5, pady=10)

        # Selected file information label
        self.selected_file_label = tk.Label(root, text="Selected File: None")
        self.selected_file_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Run button
        self.run_btn = tk.Button(root, text="Run FileFrens", command=self.run_filefrens)
        self.run_btn.grid(row=6, column=0, pady=10, columnspan=2)

        # Call the update_alias function to fetch alias-IP mappings
        self.update_alias()

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select File")
        if file_path:
            self.selected_file_label.config(text=f"Selected File: {file_path}")
            self.file_path = file_path

    def select_destination(self):
        destination_path = filedialog.askdirectory(title="Select Destination")
        if destination_path:
            self.selected_file_label.config(text=f"Selected Destination: {destination_path}")
            self.dest_path = destination_path

    def toggle_buttons(self):
        mode = self.mode_var.get()
        if mode == "sending":
            self.file_btn.config(state=tk.NORMAL)
            self.dest_btn.config(state=tk.DISABLED)
        elif mode == "receiving":
            self.file_btn.config(state=tk.DISABLED)
            self.dest_btn.config(state=tk.NORMAL)

    def run_filefrens(self):
        try:
            if hasattr(self, 'file_path'):
                mode = self.mode_var.get()
                ip = self.ip_entry.get()

                if not mode or not ip:
                    self.open_cmd_window("Please select mode and enter IP first.")
                    return

                if mode == "sending":
                    command = f"python filefrens.py -s {self.file_path} {ip}"
                elif mode == "receiving":
                    if hasattr(self, 'dest_path'):
                        command = f"python filefrens.py -r {self.dest_path} {ip}"
                    else:
                        self.open_cmd_window("Please select a destination folder.")
                        return
                else:
                    self.open_cmd_window("Invalid mode selected.")
                    return

                self.open_cmd_window(command)

            else:
                self.open_cmd_window("Please select a file first.")

        except Exception as e:
            self.open_cmd_window(f"An error occurred: {str(e)}")

    def open_cmd_window(self, command):
        subprocess.Popen(["start", "cmd", "/k", command], shell=True)

    def update_alias(self):
        url = "https://raw.githubusercontent.com/Sven-J-Steinert/FileFrens/main/alias.json"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.alias = json.loads(response.text)
                self.alias_dropdown['values'] = list(self.alias.keys())
            else:
                print(f"Failed to retrieve the file. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def update_ip_entry(self, event):
        selected_alias = self.alias_dropdown.get()
        if selected_alias in self.alias:
            selected_ip = self.alias[selected_alias]
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, selected_ip)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
