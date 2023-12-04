import tkinter as tk
from tkinter import ttk

# Function to parse the log file
def parse_log_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    cycles = {}
    integer_registers_used = set()
    mem_registers_used = set()

    # mem_registers = set()
    mem_registers = {f'M{i*8}': '0' for i in range(0, 31)}  # Initialize mem registers
    # current_cycle = None
    for line in lines:
        if line.startswith('Cycle'):
            current_cycle = int(line.split()[1][:-1])
            cycles[current_cycle] = {'reservation_stations': [], 'register_values': []}
        elif line.startswith("reservation_stations:"):
            reservation_stations = eval(line.split(':', 1)[1].strip())
            for rs in reservation_stations:
                parts = rs.split(', ')
                if parts[1] != "Idle":
                    integer_registers_used.update(filter(lambda r: r.startswith('R'), parts[4:7]))  # src1, src2, dest
                    mem_registers_used.update(filter(lambda r: r.startswith('M'), parts[4:7]))  # src1, src2, dest
            cycles[current_cycle]['reservation_stations'] = reservation_stations
        elif line.startswith("register_values:"):
            register_values = eval(line.split(':', 1)[1].strip())
            cycles[current_cycle]['register_values'] = register_values

    return cycles, integer_registers_used, mem_registers_used

# Function to create a styled Treeview for table-like data presentation
def create_table(parent, columns, show_header=True, height=100):
    tree = ttk.Treeview(parent, columns=columns, show='headings' if show_header else 'tree')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)  # Set a default width
    return tree

# Main GUI class
class TomasuloGUI:
    def __init__(self, root, log_filepath):
        self.root = root
        self.root.title("Tomasulo Simulator GUI")
        self.cycles_data, self.integer_registers_used, self.mem_registers_used = parse_log_file(log_filepath)
        self.current_cycle = 1
        self.setup_gui()

    def setup_gui(self):
        # Create frames
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        self.data_frame = tk.Frame(self.root)
        self.data_frame.pack(fill=tk.BOTH, expand=True)

        # Add control buttons
        self.prev_button = tk.Button(self.control_frame, text="Previous", command=self.prev_cycle)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.control_frame, text="Next", command=self.next_cycle)
        self.next_button.pack(side=tk.LEFT)

        self.cycle_label = tk.Label(self.control_frame, text="Current Cycle:")
        self.cycle_label.pack(side=tk.LEFT)

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_cycle)
        self.reset_button.pack(side=tk.LEFT)

        # Add tables for reservation stations, integer registers, and floating point registers
        self.rs_table = create_table(self.data_frame, ["Instr", "Name", "Stage", "Cycles Left", "Src1", "Src2", "Dest", "Vj", "Vk", "Qj", "Qk"])
        self.rs_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.int_reg_table = create_table(self.data_frame, ["Int Register", "Value"])
        self.int_reg_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.mem_reg_table = create_table(self.data_frame, ["Memory Value", "Value"])
        self.mem_reg_table.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Load initial cycle data
        self.load_cycle_data()

    def load_cycle_data(self):
        # Clear existing data in tables
        for table in [self.rs_table, self.int_reg_table, self.mem_reg_table]:
            for row in table.get_children():
                table.delete(row)

        # Load data for the current cycle
        cycle_data = self.cycles_data[self.current_cycle]
        for rs in cycle_data['reservation_stations']:
            self.rs_table.insert("", "end", values=rs.split(', '))
        for reg in cycle_data['register_values']:
            reg_name, reg_value = reg.split(', ')
            if reg_name in self.integer_registers_used:
                self.int_reg_table.insert("", "end", values=(reg_name, reg_value))
            elif reg_name in self.mem_registers_used:
                self.mem_reg_table.insert("", "end", values=(reg_name, reg_value))
    def next_cycle(self):
        if self.current_cycle < len(self.cycles_data):
            self.current_cycle += 1
            self.load_cycle_data()

    def prev_cycle(self):
        if self.current_cycle > 1:
            self.current_cycle -= 1
            self.load_cycle_data()

    def reset_cycle(self):
        self.current_cycle = 1
        self.load_cycle_data()

# Run the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    gui = TomasuloGUI(root, 'log.txt')
    root.mainloop()
