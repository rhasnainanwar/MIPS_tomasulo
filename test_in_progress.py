import json
import os


# TOMASULO Algorithms
# Class for representing an instruction
class Instruction:
    def __init__(self, instruction_str):
        # Initialize instruction components
        self.instruction_str = instruction_str.replace(',', '')  # Remove commas from instruction string
        # Initialize placeholders for various parts of the instruction
        self.op = None      # Operation type (e.g., ADD, SUB)
        self.dest = None    # Destination register
        self.src1 = None    # Source register 1
        self.src2 = None    # Source register 2
        self.immediate = None  # Immediate value (if any)
        # Placeholders for Tomasulo specific values
        self.Vj = None      # Value of source register 1
        self.Vk = None      # Value of source register 2
        self.Qj = None      # Reservation station producing source register 1 value
        self.Qk = None      # Reservation station producing source register 2 value
        self.A = None       # Used for address calculation in memory operations
        self.parse_instruction()  # Parse the instruction string

    def parse_instruction(self):
        # Parse the instruction and set the operation and operand fields
        parts = self.instruction_str.split()
        self.op = parts[0]

        # Parse based on operation type
        if self.op in ["ADD", "SUB", "MUL", "DIV"]:
            self.dest, self.src1, self.src2 = parts[1], parts[2], parts[3]
        elif self.op in ["DADDI", "DSUBI", "MULI", "DIVI"]:
            self.dest, self.src1, self.immediate = parts[1], parts[2], parts[3][1:]
        elif self.op in ["STORE", "LOAD"]:
            self.dest, self.src1, self.src2 = parts[1], parts[2], parts[3]
        elif self.op in ["BRANCH", "BEQZ", "BNEQZ"]:
            self.src1, self.A, self.src2, self.dest = parts[1], int(''.join(filter(str.isdigit, parts[2]))), "X", "X"
    def set_instruction_index(self, index):
        self.index = index

# Class for representing a register in the processor
class Register:
    def __init__(self, name, reg_type='int', value=0):
        self.name = name            # Register name
        self.reg_type = reg_type    # Register type (integer or float)
        self.is_being_written = False  # Flag to indicate if the register is being written to
        self.writing_station = None
        self.value = value          # The value stored in the register

    # Set the register as being written to
    def set_write_status(self, station = None):
        self.is_being_written = True
        self.writing_station = station

    # Clear the write status of the register
    def clear_write_status(self):
        self.is_being_written = False
        self.writing_station = None

    # Get the current write status of the register
    def get_write_status(self):
        return self.is_being_written

# Class for representing a reservation station
class ReservationStation:
    def __init__(self, name, op_type, execution_time, op_types = []):
        self.name = name               # Station name
        self.op_type = op_type         # Operation type handled by this station
        self.op_types = op_types
        self.execution_time = execution_time  # Time needed to execute an operation
        self.is_writing = False        # Flag to indicate if the station is in the write stage
        self.reset()                   # Reset the station to its initial state
    
    def assign_station(self, type):
        return True if type in self.op_types else False
    
    def perform_write(self, registers):
        # Assuming 'self.instruction' is an instance of the 'Instruction' class
        # and contains the operation (op), destination (dest), and source registers (src1, src2)
        op = self.instruction.op
        dest = self.instruction.dest
        src1 = self.instruction.src1
        src2 = self.instruction.src2

        # Assuming 'self.registers' is a dictionary storing the values of the registers
        if op == "ADD":
            registers[dest].value = self.instruction.Vj + self.instruction.Vk
        elif op == "SUB":
            registers[dest].value = self.instruction.Vj - self.instruction.Vk
        elif op == "MUL":
            registers[dest].value = self.instruction.Vj * self.instruction.Vk
        elif op == "DIV":
            registers[dest].value = self.instruction.Vj / self.instruction.Vk
        elif op == "DADDI":
            registers[dest].value = self.instruction.Vj + self.instruction.Vk
        elif op == "DSUBI":
            registers[dest].value = self.instruction.Vj - self.instruction.Vk
        elif op == "MULI":
            registers[dest].value = self.instruction.Vj * self.instruction.Vk
        elif op == "DIVI":
            registers[dest].value = self.instruction.Vj / self.instruction.Vk
        elif op in ["LOAD", "STORE"]:
            registers[dest].value = self.instruction.Vj
        # elif op in ["BRANCH", "BEQZ", "BNEQZ"]:
        #     self.branching_station = None

    # Load an instruction into the reservation station
    def load_instruction(self, instruction, index):
        self.instruction = instruction # Instruction(instruction)  # Parse and load the instruction
        self.instruction.set_instruction_index(index)
        self.stage = 'Issue'           # Set the initial stage to 'Issue'
        self.remaining_cycles = self.execution_time + 1  # Set the remaining cycles for execution

    # Reset the reservation station to its idle state
    def reset(self):
        self.busy = False              # Mark the station as not busy
        self.instruction = None        # Clear the instruction
        self.stage = "Idle"            # Set the stage to 'Idle'
        self.remaining_cycles = 0      # Reset remaining cycles

    def __str__(self):
        # String representation of the reservation station's status
        # stage = self.stage if self.instruction else "Idle"
        if self.instruction:
            stage = self.stage
            if self.instruction.src2 != None:
                return f"{self.instruction.instruction_str}, {self.name}, {stage}, {self.remaining_cycles}, {self.instruction.src1}, {self.instruction.src2}, {self.instruction.dest}, {self.instruction.Vj}, {self.instruction.Vk}, {self.instruction.Qj}, {self.instruction.Qk}"
            else:
                return f"{self.instruction.instruction_str}, {self.name}, {stage}, {self.remaining_cycles}, {self.instruction.src1}, {self.instruction.immediate}, {self.instruction.dest}, {self.instruction.Vj}, {self.instruction.Vk}, {self.instruction.Qj}, {self.instruction.Qk}"
        else:
            stage = "Idle"
            return f"{self.name}, {stage}, {self.remaining_cycles}"


# Manager class for handling multiple reservation stations
class ReservationStationManager:
    def __init__(self, station_counts, execution_times, optypes, initial_values):
        self.stations = {}             # Dictionary to store reservation stations
        self.instruction_queue = []    # Queue for holding instructions to be issued
        self.instruction_queue_index = 0 # Index
        self.issue_stage_station = None  # Current station in the issue stage
        self.write_stage_station = None  # Current station in the write stage
        self.branching_station = None # Current station in the branch
        self.initialise_registers(initial_values)  # Initialize registers with given values
        self.create_stations(station_counts, execution_times, optypes)  # Create the reservation stations

    def initialise_registers(self, initial_values):
        # Initialize general and floating-point registers and set their initial values
        # General registers
        self.registers = {f"R{i}": Register(f"R{i}") for i in range(1, 32)}
        # Floating-point registers
        self.registers.update({f"I{i}": Register(f"I{i}", 'int', i) for i in range(0, 101)})
        self.registers.update({f"M{i*8}": Register(f"M{i*8}", 'int', i) for i in range(0, 31)})


        for value in initial_values:
            # Update register values as per the provided initial values
            register_name, new_value = value.split()
            if register_name in self.registers:
                # Determine the type of the value (int or float) and update the register
                new_value = float(new_value) if register_name.startswith('F') else int(new_value)
                self.registers[register_name].value = new_value
            else:
                print(f"Register {register_name} not found.")
        self.registers["X"]  = Register("X")

    def create_stations(self, station_counts, execution_times, optypes):
        # Create reservation stations based on the given counts and execution times
        for op_type, count in station_counts.items():
            for i in range(count):
                name = f"{op_type}_{i+1}"
                self.stations[name] = ReservationStation(name, op_type, execution_times[op_type], optypes[op_type])

    def flush_stations(self, flush_index):
        for name, station in self.stations.items():
                if station.busy and station.instruction.index > flush_index:
                    station.reset()

    def add_instruction(self, instructions):
        # Add an instruction to the queue
        self.instruction_queue = instructions

    def try_issue_instruction(self):
        # Try to issue the first instruction in the queue if there are no WAW hazards
        if self.branching_station:
            return None
        if self.instruction_queue_index != len(self.instruction_queue):
            instruction = Instruction(self.instruction_queue[self.instruction_queue_index])
            write_Reg = self.registers[instruction.dest]
            if write_Reg.get_write_status():
                return None  # Stall due to WAW hazard

            for name, station in self.stations.items():
                if station.assign_station(instruction.op) and not station.busy:
                    self.instruction_queue_index+=1
                    station.load_instruction(instruction, self.instruction_queue_index)
                    print(station.name)
                    if instruction.op not in ["BRANCH", "BEQZ", "BNEQZ"]:
                        self.registers[instruction.dest].set_write_status(station.name)
                    else:
                        self.branching_station = station
                    station.busy = True
                    return station
        return None

    def execute_cycle(self):
        # Execute a cycle, handling the stages of each reservation station
        # Clear the write stage station and update the register status
        if self.write_stage_station:
            self.write_stage_station.perform_write(self.registers)
            reg = self.write_stage_station.instruction.dest
            self.registers[reg].clear_write_status()
            self.write_stage_station.reset()
            self.write_stage_station = None

        
        # TODO: add support for immediate values

        start_next_issue = True
        # Handle the issue stage station
        if self.issue_stage_station:
            #Stall execution if RAW hazard

            # Immediate Processing Case
            if not self.registers[self.issue_stage_station.instruction.src1].get_write_status() and \
                self.issue_stage_station.instruction.src2 == None:
                self.issue_stage_station.instruction.Vj = self.registers[self.issue_stage_station.instruction.src1].value
                self.issue_stage_station.instruction.Vk = int(self.issue_stage_station.instruction.immediate)
                self.issue_stage_station.instruction.Qj = None
                self.issue_stage_station.instruction.Qk = None
                self.issue_stage_station.stage = 'Execute'
                self.issue_stage_station = None

            # Normal Processing Case, when no RAW hazard
            elif not self.registers[self.issue_stage_station.instruction.src1].get_write_status() and \
                not self.registers[self.issue_stage_station.instruction.src2].get_write_status():
                self.issue_stage_station.instruction.Vj = self.registers[self.issue_stage_station.instruction.src1].value
                self.issue_stage_station.instruction.Vk = self.registers[self.issue_stage_station.instruction.src2].value
                self.issue_stage_station.instruction.Qj = None
                self.issue_stage_station.instruction.Qk = None
                self.issue_stage_station.stage = 'Execute'
                self.issue_stage_station = None
            else:
                if self.registers[self.issue_stage_station.instruction.src1].writing_station == self.issue_stage_station.name:
                    self.issue_stage_station.instruction.Vj = self.registers[self.issue_stage_station.instruction.src1].value
                    self.issue_stage_station.instruction.Qj = None

                if self.issue_stage_station.instruction.src2 and self.registers[self.issue_stage_station.instruction.src2].writing_station == self.issue_stage_station.name:
                    self.issue_stage_station.instruction.Vk = self.registers[self.issue_stage_station.instruction.src2].value
                    self.issue_stage_station.instruction.Qk = None

                if self.issue_stage_station.instruction.Qj == None and self.issue_stage_station.instruction.Qk == None:
                    self.issue_stage_station.stage = 'Execute'
                    self.issue_stage_station = None
                else:
                    start_next_issue = False  
                

        # Attempt to issue an instruction if possible
        if start_next_issue:
            self.issue_stage_station = self.try_issue_instruction()
            if self.issue_stage_station:
                if self.registers[self.issue_stage_station.instruction.src1].get_write_status():
                    self.issue_stage_station.instruction.Vj = self.issue_stage_station.instruction.src1
                    self.issue_stage_station.instruction.Qj = self.registers[self.issue_stage_station.instruction.src1].writing_station
                else:
                    self.issue_stage_station.instruction.Vj = self.registers[self.issue_stage_station.instruction.src1].value
                    self.issue_stage_station.instruction.Qj = None

                if self.issue_stage_station.instruction.src2 == None:
                    self.issue_stage_station.instruction.Vk = int(self.issue_stage_station.instruction.immediate)
                    self.issue_stage_station.instruction.Qk = None
                elif self.registers[self.issue_stage_station.instruction.src2].get_write_status():
                    self.issue_stage_station.instruction.Vk = self.issue_stage_station.instruction.src2
                    self.issue_stage_station.instruction.Qk = self.registers[self.issue_stage_station.instruction.src2].writing_station
                else:
                    self.issue_stage_station.instruction.Vk =self.registers[ self.issue_stage_station.instruction.src2].value
                    self.issue_stage_station.instruction.Qk = None
       

        all_stations_idle = True
        # Process each reservation station
        for name, station in self.stations.items():
            if station.instruction:
                # Handle the execute stage
                if station.stage == 'Execute':
                    if station.remaining_cycles > 1:
                        station.remaining_cycles -= 1
                    elif not self.write_stage_station:
                        if station.instruction.op not in ["BRANCH", "BEQZ", "BNEQZ"]:
                            station.stage = 'Write'
                            station.remaining_cycles -= 1
                            self.write_stage_station = station
                        else:
                        
                            for name, station in self.stations.items():
                                if station.busy and station.instruction.index < self.instruction_queue_index:
                                    all_stations_idle = False
                                    break
                            if not all_stations_idle:
                                continue     
                            elif station.instruction.op == "BRANCH":
                                # self.flush_stations(self.instruction_queue_index)
                                self.instruction_queue_index = station.instruction.A
                                self.branching_station = None
                                station.reset()
                            
                            elif station.instruction.op == "BEQZ":
                                if self.registers[station.instruction.src1].value == 0:
                                    # self.flush_stations(self.instruction_queue_index)
                                    self.instruction_queue_index = station.instruction.A
                                self.branching_station = None
                                station.reset()

                            elif station.instruction.op == "BNEQZ":
                                if self.registers[station.instruction.src1].value != 0:
                                    # self.flush_stations(self.instruction_queue_index)
                                    self.instruction_queue_index = station.instruction.A
                                station.reset()
                                self.branching_station = None



                            # Perform Branch


            if station.stage != "Idle":
                all_stations_idle = False

        return all_stations_idle

    def get_station_statuses(self):
        # Return the current status of each reservation station
        return {name: str(station) for name, station in self.stations.items()}

# Execution times and station counts for different instruction types
execution_times = {"ADD": 4, "MUL": 1, "DIV": 40, "STORE": 3, "BRANCH": 3}
station_counts = {"ADD": 2, "MUL": 2, "DIV": 1, "STORE": 2, "BRANCH": 1}
optypes = { "ADD": ["ADD", "SUB", "DADDI", "DSUBI"],
           "MUL": ["MUL", "MULI"],
           "DIV": ["DIV", "DIVI"],
           "STORE": ["STORE", "LOAD"],
           "BRANCH": ["BRANCH", "BEQZ", "BNEQZ"]}

# Initialize the Reservation Station Manager with initial register values
initial_values = ["R1 80", "R2 10", "R3 80", "R4 20", "R5 5", "R6 10", "R7 16",
                  "M0 10", "M8 16", "M16 32", "M24 64", "M32 128"]
# initial_values = ["M0 8", "M8 16", "M16 32", "M24 64", "M32 128"]

rs_manager = ReservationStationManager(station_counts, execution_times, optypes, initial_values)

# List of instructions to be issued
# instructions = ["SUB R1, R2, R3", "ADD R1, R2, R3", "ADD R7, R3, R3", "ADD R2, R7, R3", "MUL R4, R2, R6", "ADD R4, R8, R7"]
# instructions = ["ADD R1, R1, R3", "ADD R4, R5, R3", "DSUBI R10, R1, #100"]
instructions = ["LOAD R2, M0, X", "DADDI R4, R2, #10",  "ADD R1, R4, R3", "ADD R1, R1, R6", "SUB R6, R6, R5","DSUBI R10, R1, #100", "BNEQZ R10, 0, #0",  "STORE M8, R5, X"]
# instructions = ["ADD R1, R1, R2", "BNEQZ R10, 0, X", "LOAD R1, M8, X"]


# instructions = ["LOAD R1, M8, X",  "DADDI R5, R5, #100", "STORE M8, R5, X", "DSUBI R10, R1, #100"]

rs_manager.add_instruction(instructions)



# Add all instructions to the manager's queue right away


def log_rs_manager_state(rs_manager, cycle, base_file_name="log"):
    """
    Logs the state of rs_manager to a file. Creates a new file on the first iteration and appends to it on subsequent iterations.

    Args:
    rs_manager: The reservation station manager object.
    cycle: The current cycle number.
    base_file_name: The base name for the log file.
    """
    # Determine file names
    text_file_name = f"{base_file_name}.txt"
    json_file_name = f"{base_file_name}.json"

    # Extracting the state of each reservation station
    stations_data_txt = []
    for name, station in rs_manager.stations.items():
        stations_data_txt.append(str(station))
    stations_data_json = [str(station) for station in rs_manager.stations]
    
    # Extracting the values of all registers
    registers_data_txt = [f"{name}, {reg.value}" for name, reg in rs_manager.registers.items()]

    # Constructing the log data
    log_data = {
        # "cycle": cycle,
        "reservation_stations": stations_data_txt,
        "register_values": registers_data_txt
    }

    # Open the file in append mode if it's not the first cycle, else in write mode
    mode = "a" if cycle > 1 else "w"

    # Writing to the text file
    with open(text_file_name, mode) as file:
        file.write(f"Cycle {cycle}:\n")
        for key, value in log_data.items():
            file.write(f"{key}: {value}\n")
        file.write("\n")  # Adding a newline for separation between cycles

    # Writing to the JSON file
    with open(json_file_name, mode) as file:
        if cycle == 1:
            file.write("[")  # Start of JSON array
        else:
            file.write(",\n")  # Separator between JSON objects
        json.dump(log_data, file, indent=4)
        if cycle == 1:
            file.write("\n")  # End of JSON array

    print(f"Logged rs_manager data for cycle {cycle} to {text_file_name} and {json_file_name}")

# Simulate execution cycles
cycle = 0
log_rs_manager_state(rs_manager, cycle)

while True:
    
    log_rs_manager_state(rs_manager, cycle)
    cycle += 1
    all_idle = rs_manager.execute_cycle()
    # print(f"Cycle {cycle}:")
    for station, status in rs_manager.get_station_statuses().items():
        print(f"  {status} ")

    if all_idle and rs_manager.instruction_queue_index == len(rs_manager.instruction_queue):
        log_rs_manager_state(rs_manager, cycle)
        break

print("All instructions have been processed.")
