# Thorlabs Optical Power Meter Interface for Pulsed Laser Power Calculations

A Python-based interface for Thorlabs optical power meters with dedicated support for pulsed laser measurements. This tool enables both **real-time monitoring** and **on-demand calculations** of peak power for pulsed laser systems.

### Features

* Live data acquisition from supported Thorlabs optical power meters
* Automatic **peak power calculation** while the power meter is running
* Manual peak power calculation with a single click when the meter is idle
* Adjustable pulse parameters (repetition rate, pulse width) for accurate computation
* Tkinter-based GUI for intuitive control and visualization
* Continuous display of measured power and calculated peak power

### Use Cases

* Research labs performing pulsed laser characterization
* Optical system alignment and diagnostics
* Educational demonstrations of pulsed vs. CW laser power behavior

### Requirements

* Python 3.x
* Thorlabs Optical Power Meter with NI-Visa drivers. Not TLPM.
* `ThorlabsPM100` (or appropriate device library)
* 'tkinter', 'pyvisa', 'ThorlabsPM100', 'threading'
