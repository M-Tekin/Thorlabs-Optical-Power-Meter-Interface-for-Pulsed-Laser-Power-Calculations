# Muhammet Tekin

import tkinter as tk
from tkinter import ttk
from ThorlabsPM100 import ThorlabsPM100
import pyvisa
import threading


class PowerMeterApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.meter = None
        self.zeroed_value = None  # Store the zeroed value

        self.root.title("MTekin")
        self.root.geometry("400x400")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.tab1 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="Peak Power Calculator")
        self.notebook.add(self.tab4, text="Power Meter Settings")

        self.create_tab1_content(self.tab1)
        self.create_power_meter_settings_tab(self.tab4)

    def read_power_meter(self):
        try:
            if not self.meter:
                rm = pyvisa.ResourceManager()
                inst = rm.open_resource('USB0::0x1313::0x8076::M00642985::INSTR')
                self.meter = ThorlabsPM100(inst=inst)

                # Ensure the range upper limit is set correctly
                self.meter.sense.power.dc.range.upper = self.meter.sense.power.dc.range.maximum_upper

            if self.running:
                power = self.meter.read  # Ensure this is a method call, not just accessing a float
                if self.zeroed_value is not None:
                    power -= self.zeroed_value  # Subtract the zeroed value

                self.avg_power_entry.delete(0, tk.END)
                self.avg_power_entry.insert(0, f"{power:.10f}")
                
                # Automatically calculate peak power when the power meter is running
                self.calculate_peak_power(auto=True)
                
                self.root.after(500, self.read_power_meter)  # Update every 500ms
        except Exception as e:
            print(f"Error reading power meter: {e}")

    def start_measurement(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.read_power_meter, daemon=True).start()

    def stop_measurement(self):
        self.running = False

    def calculate_peak_power(self, auto=False):
        """Calculate peak power either automatically or manually."""
        try:
            avg_power = float(self.avg_power_entry.get())
            frequency_str = self.frequency_entry.get().strip()
            pulse_width_str = self.pulse_width_entry.get().strip()
            attenuation_text = self.attenuation_entry.get().strip()

            if not frequency_str or not pulse_width_str:
                self.result_label.config(text="Please fill in all fields")
                return

            frequency = float(frequency_str)
            pulse_width = float(pulse_width_str)

            # Unit conversion multipliers
            unit_multipliers = {
                "W": 1, "mW": 1e-3, "µW": 1e-6,
                "Hz": 1, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9,
                "s": 1, "ms": 1e-3, "µs": 1e-6, "ns": 1e-9
            }

            # Apply unit conversion for frequency and pulse width
            avg_power *= unit_multipliers[self.avg_power_unit.get()]
            frequency *= unit_multipliers[self.frequency_unit.get()]
            pulse_width *= unit_multipliers[self.pulse_width_unit.get()]

            # Handle attenuation if present
            if attenuation_text:
                try:
                    attenuation = float(attenuation_text) / 100  # Convert percentage to fraction
                except ValueError:
                    self.result_label.config(text="Invalid attenuation value")
                    return
                peak_power = (avg_power / (frequency * pulse_width *attenuation))
            else:
                peak_power = avg_power / (frequency * pulse_width)

            # Update the result label with the calculated peak power
            if auto:
                # Automatically calculate peak power while the power meter is running
                self.result_label.config(text=f"Peak Power: {peak_power:.2f} W")
            else:
                self.result_label.config(text=f"Peak Power: {peak_power:.2f} W")
                
        except ValueError:
            self.result_label.config(text="Invalid input, please enter valid numbers")

    def on_wavelength_change(self, event=None):
        """Update the wavelength on the power meter when the wavelength entry is changed."""
        try:
            # Check if wavelength is empty, and if so, set it to 905 nm
            wavelength = self.wavelength_entry.get().strip()
            if not wavelength:
                wavelength = 905  # Default wavelength if the field is empty
                self.wavelength_entry.delete(0, tk.END)
                self.wavelength_entry.insert(0, str(wavelength))  # Insert default value

            # Convert the wavelength to float
            wavelength = float(wavelength)

            # Update the wavelength on the power meter
            if self.meter:
                self.meter.sense.correction.wavelength = wavelength  # Set the wavelength on the meter
                print(f"Wavelength set to {wavelength} nm")  # For debugging

        except ValueError:
            print("Invalid wavelength input")

    def create_tab1_content(self, tab):
        units_power = ["W", "mW", "µW"]
        units_freq = ["Hz", "kHz", "MHz", "GHz"]
        units_time = ["s", "ms", "µs", "ns"]

        ttk.Label(tab, text="Average Power:").grid(row=0, column=0, pady=2, padx=5)
        self.avg_power_entry = ttk.Entry(tab)  # Make avg_power_entry a class attribute
        self.avg_power_entry.grid(row=0, column=1)
        self.avg_power_unit = ttk.Combobox(tab, values=units_power, state="readonly")
        self.avg_power_unit.grid(row=0, column=2)
        self.avg_power_unit.current(1)  # Default to mW

        ttk.Label(tab, text="Frequency:").grid(row=1, column=0, pady=2, padx=5)
        self.frequency_entry = ttk.Entry(tab)
        self.frequency_entry.grid(row=1, column=1)
        self.frequency_unit = ttk.Combobox(tab, values=units_freq, state="readonly")
        self.frequency_unit.grid(row=1, column=2)
        self.frequency_unit.current(0)  # Default to Hz

        ttk.Label(tab, text="Pulse Width:").grid(row=2, column=0, pady=2, padx=5)
        self.pulse_width_entry = ttk.Entry(tab)
        self.pulse_width_entry.grid(row=2, column=1)
        self.pulse_width_unit = ttk.Combobox(tab, values=units_time, state="readonly")
        self.pulse_width_unit.grid(row=2, column=2)
        self.pulse_width_unit.current(3)  # Default to ns

        ttk.Label(tab, text="Attenuation (%):").grid(row=3, column=0, pady=2, padx=5)
        self.attenuation_entry = ttk.Entry(tab)
        self.attenuation_entry.grid(row=3, column=1)

        self.result_label = ttk.Label(tab, text="Peak Power: ")
        self.result_label.grid(row=4, column=0, columnspan=3, pady=10)

        calc_button = ttk.Button(tab, text="Calculate", command=self.calculate_peak_power)
        calc_button.grid(row=5, column=0, columnspan=3, pady=5)

        zero_button = ttk.Button(tab, text="Zero", command=self.zero)
        zero_button.grid(row=6, column=0, columnspan=3, pady=5)

        reset_button = ttk.Button(tab, text="Reset Zero", command=self.reset_zero)
        reset_button.grid(row=7, column=0, columnspan=3, pady=5)

        # Label to show the zeroed value
        self.zeroed_value_label = ttk.Label(tab, text="Zeroed Value: None")
        self.zeroed_value_label.grid(row=8, column=0, columnspan=3, pady=5)

    def zero(self):
        """Set the current average power reading as the zeroed value."""
        try:
            self.zeroed_value = float(self.avg_power_entry.get())
            self.zeroed_value_label.config(text=f"Zeroed Value: {self.zeroed_value:.10f}")
            print(f"Zeroed value set to: {self.zeroed_value}")
        except ValueError:
            print("Invalid average power value for zeroing")

    def reset_zero(self):
        """Reset the zeroed value."""
        self.zeroed_value = None
        self.zeroed_value_label.config(text="Zeroed Value: None")
        print("Zero value reset")

    def create_power_meter_settings_tab(self, tab):
        ttk.Label(tab, text="Power Meter Settings").pack(pady=5)

        warning_label = ttk.Label(tab, text="This feature only works with Thorlabs PM10xxxxxx Power Meter Consoles which have NI-VISA drivers!", 
                              foreground="red", wraplength=270)
        warning_label.pack(pady=5)

        ttk.Label(tab, text="Wavelength (nm):").pack()
        self.wavelength_entry = ttk.Entry(tab)  # Make wavelength_entry a class attribute
        self.wavelength_entry.pack()
        self.wavelength_entry.insert(0, "905")  # Set default wavelength to 905 nm if it's empty
        self.wavelength_entry.bind("<FocusOut>", self.on_wavelength_change)  # Bind the change event

        ttk.Label(tab, text="Averaging Count:").pack()  # Replaced "Resolution" with "Averaging Count"
        self.averaging_entry = ttk.Entry(tab)  # Averaging count entry
        self.averaging_entry.pack()

        # Set default value to 100 if empty
        self.averaging_entry.insert(0, "100")  # Set default averaging value to 100

        start_button = ttk.Button(tab, text="Start Measurement", command=self.start_measurement)
        start_button.pack(pady=5)

        stop_button = ttk.Button(tab, text="Stop Measurement", command=self.stop_measurement)
        stop_button.pack(pady=5)

        # When the averaging value is changed, it will update the meter's averaging count
        self.averaging_entry.bind("<FocusOut>", self.update_averaging)

    def start_measurement(self):
        # Get the latest wavelength value and update the power meter if not already updated
        wavelength_str = self.wavelength_entry.get().strip()
        if not wavelength_str:
            wavelength_str = "905"  # Set default wavelength if empty
            self.wavelength_entry.insert(0, wavelength_str)  # Insert default value

        try:
            wavelength = float(wavelength_str)
            if self.meter:
                self.meter.sense.correction.wavelength = wavelength
                print(f"Wavelength set to {wavelength} nm")
        except ValueError:
            print("Invalid wavelength input")

        # Get the latest averaging count value and update the power meter
        averaging_str = self.averaging_entry.get().strip()
        if not averaging_str:
            averaging_str = "100"  # Default averaging value if not provided
            self.averaging_entry.insert(0, averaging_str)  # Insert default value

        try:
            averaging_count = int(averaging_str)
            if self.meter:
                self.meter.sense.average.count = averaging_count
                print(f"Averaging count set to {averaging_count}")
        except ValueError:
            print("Invalid averaging count input")

        if not self.running:
            self.running = True
            threading.Thread(target=self.read_power_meter, daemon=True).start()

    def update_averaging(self, event=None):
        """Update the averaging count on the power meter."""
        try:
            averaging_count = int(self.averaging_entry.get())
            if self.meter:
                self.meter.sense.average.count = averaging_count  # Set the averaging count
                print(f"Averaging count set to: {averaging_count}")
        except ValueError:
            print("Invalid averaging count value")


if __name__ == "__main__":
    root = tk.Tk()
    app = PowerMeterApp(root)
    root.mainloop()
