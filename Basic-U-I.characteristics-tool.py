import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Ensure LaTeX rendering is disabled
plt.rcParams["text.usetex"] = False

# Unit conversion factors for voltage, current, and resistance
unit_factors = {'V': 1, 'mV': 0.001, 'µV': 1e-6, 'kV': 1000}
current_factors = {'A': 1, 'mA': 0.001, 'µA': 1e-6, 'kA': 1000}
resistance_factors = {'Ω': 1, 'mΩ': 0.001, 'µΩ': 1e-6, 'kΩ': 1000, 'GΩ': 1e9}

def update_plot():
    """Update the plot for resistor characteristics."""
    try:
        # Voltage and current range
        u_min = float(u_min_var.get())
        u_max = float(u_max_var.get())
        i_min = float(i_min_var.get())
        i_max = float(i_max_var.get())

        # Unit conversion factors
        u_factor = unit_factors[u_unit_var.get()]
        i_factor = current_factors[i_unit_var.get()]

        # Resistor values
        r1 = float(r1_var.get()) * resistance_factors[r1_unit_var.get()]
        r2 = float(r2_var.get()) * resistance_factors[r2_unit_var.get()]
        r3 = float(r3_var.get()) * resistance_factors[r3_unit_var.get()]

        # Calculate data for the lines
        voltages = [u for u in range(int(u_min * u_factor), int(u_max * u_factor) + 1)]
        i_r1 = [u / r1 for u in voltages]
        i_r2 = [u / r2 for u in voltages]
        i_r3 = [u / r3 for u in voltages]

        # Update the plot
        ax.clear()
        ax.plot(
            [v / u_factor for v in voltages], 
            [i / i_factor for i in i_r1], 
            label=f'R1 = {r1 / resistance_factors["Ω"]} Ω'
        )
        ax.plot(
            [v / u_factor for v in voltages], 
            [i / i_factor for i in i_r2], 
            label=f'R2 = {r2 / resistance_factors["Ω"]} Ω'
        )
        ax.plot(
            [v / u_factor for v in voltages], 
            [i / i_factor for i in i_r3], 
            label=f'R3 = {r3 / resistance_factors["Ω"]} Ω'
        )
        ax.set_xlim(u_min, u_max)
        ax.set_ylim(i_min, i_max)
        ax.set_xlabel(f"U / {u_unit_var.get()}")
        ax.set_ylabel(f"I / {i_unit_var.get()}")
        ax.grid(which='major', linestyle='--', linewidth=0.5)
        
        if show_secondary_grid.get():
            ax.minorticks_on()
            ax.grid(which='minor', linestyle=':', linewidth=0.5)
        else:
            ax.minorticks_off()

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
        canvas.draw()
    except Exception as e:
        print(f"Error: {e}")

def update_plot_tab2():
    """Update the plot for the voltage source characteristics."""
    try:
        # Get voltage source and resistor values
        uq = float(uq_var.get()) * unit_factors[uq_unit_var.get()]
        ri = float(ri_var.get()) * resistance_factors[ri_unit_var.get()]
        rl = float(rl_var.get()) * resistance_factors[rl_unit_var.get()]

        # Calculate currents and voltages
        currents = [i / 10 for i in range(0, 110)]
        voltages = [uq - i * ri for i in currents]

        ax_tab2.clear()
        ax_tab2.plot(voltages, currents, label="Voltage Source (Uq, Ri)")

        if show_rl.get():
            vl_rl = [i * rl for i in currents]
            ax_tab2.plot(currents, vl_rl, label="Load Resistor (RL)")

            ap_found = False
            for i, (v_q, v_rl) in enumerate(zip(voltages, vl_rl)):
                if abs(v_q - v_rl) < 0.1:
                    ax_tab2.scatter(currents[i], v_q, color="red", label=f"AP: U={v_q:.2f} V, I={currents[i]:.2f} A")
                    ap_found = True
                    break

            if not ap_found:
                print("Operating Point not found. Check the input values!")

            if ap_found:
                ap_voltage_var.set(f"{v_q:.2f} V")
                ap_current_var.set(f"{currents[i]:.2f} A")
            else:
                ap_voltage_var.set("N/A")
                ap_current_var.set("N/A")

        ax_tab2.set_ylim(0, max(currents))
        ax_tab2.set_xlim(0, uq)
        ax_tab2.set_ylabel("I / A")
        ax_tab2.set_xlabel("U / V")
        ax_tab2.grid(which='major', linestyle='--', linewidth=0.5)

        if show_secondary_grid_tab2.get():
            ax_tab2.minorticks_on()
            ax_tab2.grid(which='minor', linestyle=':', linewidth=0.5)
        else:
            ax_tab2.minorticks_off()

        canvas_tab2.draw()
    except Exception as e:
        print(f"Error: {e}")

# Main window
root = tk.Tk()
root.title("I-U Diagram Generator")

# Create tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Tab 1: Resistor characteristics
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Resistor Characteristics")

# Input frame for Tab 1
frame = ttk.Frame(tab1)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Voltage input
ttk.Label(frame, text="Voltage range (U):").grid(row=0, column=0, sticky="w")
u_min_var = tk.StringVar(value="0")
u_max_var = tk.StringVar(value="10")
ttk.Entry(frame, textvariable=u_min_var, width=5).grid(row=0, column=1)
ttk.Label(frame, text="to").grid(row=0, column=2)
ttk.Entry(frame, textvariable=u_max_var, width=5).grid(row=0, column=3)
u_unit_var = tk.StringVar(value="V")
ttk.Combobox(frame, textvariable=u_unit_var, values=["V", "mV", "µV", "kV"], width=5).grid(row=0, column=4)

# Current input
ttk.Label(frame, text="Current range (I):").grid(row=1, column=0, sticky="w")
i_min_var = tk.StringVar(value="0")
i_max_var = tk.StringVar(value="100")
ttk.Entry(frame, textvariable=i_min_var, width=5).grid(row=1, column=1)
ttk.Label(frame, text="to").grid(row=1, column=2)
ttk.Entry(frame, textvariable=i_max_var, width=5).grid(row=1, column=3)
i_unit_var = tk.StringVar(value="mA")
ttk.Combobox(frame, textvariable=i_unit_var, values=["A", "mA", "µA", "kA"], width=5).grid(row=1, column=4)

# Resistor input
ttk.Label(frame, text="Resistor values (R):").grid(row=2, column=0, sticky="w")
r1_var = tk.StringVar(value="100")
r2_var = tk.StringVar(value="200")
r3_var = tk.StringVar(value="500")
r1_unit_var = tk.StringVar(value="Ω")
r2_unit_var = tk.StringVar(value="Ω")
r3_unit_var = tk.StringVar(value="Ω")
ttk.Entry(frame, textvariable=r1_var, width=10).grid(row=2, column=1)
ttk.Combobox(frame, textvariable=r1_unit_var, values=["Ω", "mΩ", "µΩ", "kΩ", "GΩ"], width=5).grid(row=2, column=2)
ttk.Entry(frame, textvariable=r2_var, width=10).grid(row=3, column=1)
ttk.Combobox(frame, textvariable=r2_unit_var, values=["Ω", "mΩ", "µΩ", "kΩ", "GΩ"], width=5).grid(row=3, column=2)
ttk.Entry(frame, textvariable=r3_var, width=10).grid(row=4, column=1)
ttk.Combobox(frame, textvariable=r3_unit_var, values=["Ω", "mΩ", "µΩ", "kΩ", "GΩ"], width=5).grid(row=4, column=2)
ttk.Label(frame, text="R1:").grid(row=2, column=3)
ttk.Label(frame, text="R2:").grid(row=3, column=3)
ttk.Label(frame, text="R3:").grid(row=4, column=3)

# Secondary grid option
show_secondary_grid = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="Show secondary grid", variable=show_secondary_grid).grid(row=5, column=0, columnspan=5)

# Plot for Tab 1
fig = Figure(figsize=(6, 4))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=tab1)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Toolbar for Tab 1
toolbar = NavigationToolbar2Tk(canvas, tab1)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Update plot button
ttk.Button(frame, text="Update Diagram", command=update_plot).grid(row=6, column=0, columnspan=5)

# Tab 2: Voltage source characteristics
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Voltage Source Characteristics")

# Input frame for Tab 2
frame_tab2 = ttk.Frame(tab2)
frame_tab2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Voltage source input
ttk.Label(frame_tab2, text="Source Voltage (Uq):").grid(row=0, column=0, sticky="w")
uq_var = tk.StringVar(value="10")
uq_unit_var = tk.StringVar(value="V")
ttk.Entry(frame_tab2, textvariable=uq_var, width=10).grid(row=0, column=1)
ttk.Combobox(frame_tab2, textvariable=uq_unit_var, values=["V", "mV", "µV", "kV"], width=5).grid(row=0, column=2)

# Internal resistance input
ttk.Label(frame_tab2, text="Internal Resistance (Ri):").grid(row=1, column=0, sticky="w")
ri_var = tk.StringVar(value="1")
ri_unit_var = tk.StringVar(value="Ω")
ttk.Entry(frame_tab2, textvariable=ri_var, width=10).grid(row=1, column=1)
ttk.Combobox(frame_tab2, textvariable=ri_unit_var, values=["Ω", "mΩ", "µΩ", "kΩ", "GΩ"], width=5).grid(row=1, column=2)

# Load resistor input
ttk.Label(frame_tab2, text="Load Resistance (RL):").grid(row=2, column=0, sticky="w")
rl_var = tk.StringVar(value="10")
rl_unit_var = tk.StringVar(value="Ω")
ttk.Entry(frame_tab2, textvariable=rl_var, width=10).grid(row=2, column=1)
ttk.Combobox(frame_tab2, textvariable=rl_unit_var, values=["Ω", "mΩ", "µΩ", "kΩ", "GΩ"], width=5).grid(row=2, column=2)

# Secondary grid option for Tab 2
show_secondary_grid_tab2 = tk.BooleanVar(value=False)
ttk.Checkbutton(frame_tab2, text="Show secondary grid", variable=show_secondary_grid_tab2).grid(row=4, column=0, columnspan=5)

# Show load resistor checkbox
show_rl = tk.BooleanVar(value=False)
ttk.Checkbutton(frame_tab2, text="Show load resistor", variable=show_rl).grid(row=3, column=0, columnspan=3)

# Operating point display
ttk.Label(frame_tab2, text="Operating Point (OP):").grid(row=7, column=0, sticky="w")
ttk.Label(frame_tab2, text="Voltage (U):").grid(row=8, column=0, sticky="w")
ap_voltage_var = tk.StringVar(value="N/A")
ttk.Label(frame_tab2, textvariable=ap_voltage_var).grid(row=9, column=1, sticky="w")

ttk.Label(frame_tab2, text="Current (I):").grid(row=10, column=0, sticky="w")
ap_current_var = tk.StringVar(value="N/A")
ttk.Label(frame_tab2, textvariable=ap_current_var).grid(row=11, column=1, sticky="w")

# Plot for Tab 2
fig_tab2 = Figure(figsize=(6, 4))
ax_tab2 = fig_tab2.add_subplot(111)
canvas_tab2 = FigureCanvasTkAgg(fig_tab2, master=tab2)
canvas_tab2.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Toolbar for Tab 2
toolbar_tab2 = NavigationToolbar2Tk(canvas_tab2, tab2)
toolbar_tab2.update()
canvas_tab2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Update plot button
ttk.Button(frame_tab2, text="Update Diagram", command=update_plot_tab2).grid(row=5, column=0, columnspan=3)

# Initialize the GUI
update_plot()
root.mainloop()
