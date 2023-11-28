import tkinter as tk
from tkinter import ttk

# Function to create a styled Treeview for table-like data presentation
def create_table(parent, columns, show_header=True, height = 100):
    tree = ttk.Treeview(parent, columns=columns, show='headings' if show_header else 'tree')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)  # Set a default width
    return tree


root = tk.Tk()
root.title("Tomasulo Simulator GUI")

# Define fonts and colors
heading_font = ('Helvetica', 14, 'bold')
data_font = ('Helvetica', 12)
bg_color = 'white'
fg_color = 'black'
heading_bg_color = '#7B68EE'

# Define fonts and colors
heading_font = ('Helvetica', 14, 'bold')
data_font = ('Helvetica', 12)  # Larger font for other widgets
small_font = ('Helvetica', 8)  # Smaller font for Treeview



# Instruction Status Frame
instr_status_frame = tk.LabelFrame(root, text="Instruction Execution Sequence", font=heading_font, bg=heading_bg_color, fg=fg_color)
instr_status_frame.pack(side="top", fill="x", expand=True)

# Table 1 for Instruction Status (First half of the columns)
instr_status_table1 = create_table(instr_status_frame, ('ITER', 'Instruction', 'dest', 'j', 'k'))
instr_status_table1.pack(side="left", fill="x", expand=True)

# Table 2 for Instruction Status (Second half of the columns)
instr_status_table2 = create_table(instr_status_frame, ('Issue', 'Exec Start', 'Exec Comp', 'Write Result'))
instr_status_table2.pack(side="left", fill="x", expand=True)

# Reservation Stations Frame
res_stations_frame = tk.LabelFrame(root, text="Reservation Stations", font=heading_font, bg=heading_bg_color, fg=fg_color)
res_stations_frame.pack(side="top", fill="x", expand=False)

# Table for Reservation Stations
res_stations_table = create_table(res_stations_frame, ('Time', 'Name', 'Busy', 'Op', 'Vj', 'Vk', 'Qj', 'Qk'))
res_stations_table.pack(side="top", fill="x", expand=True)

status_container_frame = tk.Frame(root)
status_container_frame.pack(side="top", fill="x", expand=True)

# Clock Frame
clock_frame = tk.LabelFrame(status_container_frame, text="Clock", font=heading_font, bg=heading_bg_color, fg=fg_color)
clock_frame.pack(side="left", fill="x", expand=True)

# Table for Clock
clock_table = create_table(clock_frame, ('Cycle',))
clock_table.pack(fill="both", expand=True)


# Register Result Status Container Frame
reg_result_container_frame = tk.Frame(status_container_frame)
reg_result_container_frame.pack(side="left", fill="x", expand=True)

# Floating Point Register Result Status Frame
fp_reg_result_status_frame = tk.LabelFrame(reg_result_container_frame, text="Floating Point Register Result Status", font=heading_font, bg=heading_bg_color, fg=fg_color)
fp_reg_result_status_frame.pack(side="top", fill="x", expand=True)

# Table for Floating Point Register Result Status
fp_reg_result_status_table = create_table(fp_reg_result_status_frame, ('F0', 'F2', 'F4', 'F6', 'F8', 'F10', 'F12', '...'))
fp_reg_result_status_table.pack(fill="both", expand=True)

# Integer Register Result Status Frame
int_reg_result_status_frame = tk.LabelFrame(reg_result_container_frame, text="Integer Register Result Status", font=heading_font, bg=heading_bg_color, fg=fg_color)
int_reg_result_status_frame.pack(side="top", fill="x", expand=True)

# Table for Integer Register Result Status
int_reg_result_status_table = create_table(int_reg_result_status_frame, ('R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', '...'))
int_reg_result_status_table.pack(fill="both", expand=True)

# Code Section Frame
code_section_frame = tk.LabelFrame(root, text="Buttons", font=heading_font, bg=heading_bg_color, fg=fg_color)
code_section_frame.pack(side="top", fill="both", expand=True)

# Split the Code Section Frame into two columns: one for text and one for buttons
code_text_frame = tk.Frame(code_section_frame)
# code_text_frame.pack(side="left", fill="both", expand=True)
buttons_frame = tk.Frame(code_section_frame)
buttons_frame.pack(side="left", fill="both", expand=True)

# Text Box for Code Section (Left half)
code_text = tk.Text(code_text_frame, height=5, width=50, font=data_font)  # Adjust width as needed
code_text.pack(side="top", fill="both", expand=True)

# Buttons (Right half)
prev_button = tk.Button(buttons_frame, text="Previous", command=lambda: None)  # Replace None with the actual command
prev_button.pack(side="top", pady=5)

next_button = tk.Button(buttons_frame, text="Next", command=lambda: None)  # Replace None with the actual command
next_button.pack(side="top", pady=5)

reset_button = tk.Button(buttons_frame, text="Reset", command=lambda: None)  # Replace None with the actual command
reset_button.pack(side="top", pady=5)

root.mainloop()
