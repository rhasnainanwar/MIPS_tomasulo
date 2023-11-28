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
            # For arithmetic instructions
            self.dest, self.src1, self.src2 = parts[1], parts[2], parts[3]
        elif self.op in ["STORE", "LOAD"]:
            # For memory operations
            self.src1, offset_reg = parts[1], parts[2]
            self.immediate, self.src2 = offset_reg.split('(')
            self.src2 = self.src2[:-1]  # Removing the closing parenthesis
        elif self.op == "BRANCH":
            # For branch instructions
            self.src1, self.src2, self.immediate = parts[1], parts[2], parts[3]

# Class for representing a register in the processor
class Register:
    def __init__(self, name, reg_type='int', value=0):
        self.name = name            # Register name
        self.reg_type = reg_type    # Register type (integer or float)
        self.is_being_written = False  # Flag to indicate if the register is being written to
        self.value = value          # The value stored in the register

    # Set the register as being written to
    def set_write_status(self):
        self.is_being_written = True

    # Clear the write status of the register
    def clear_write_status(self):
        self.is_being_written = False

    # Get the current write status of the register
    def get_write_status(self):
        return self.is_being_written

# Class for representing a reservation station
class ReservationStation:
    def __init__(self, name, op_type, execution_time):
        self.name = name               # Station name
        self.op_type = op_type         # Operation type handled by this station
        self.execution_time = execution_time  # Time needed to execute an operation
        self.is_writing = False        # Flag to indicate if the station is in the write stage
        self.reset()                   # Reset the station to its initial state

    # Load an instruction into the reservation station
    def load_instruction(self, instruction):
        self.instruction = Instruction(instruction)  # Parse and load the instruction
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
        stage = self.stage if self.instruction else "Idle"
        return f"RS[{self.name}]: {stage} ({self.remaining_cycles})"

# Manager class for handling multiple reservation stations
class ReservationStationManager:
    def __init__(self, station_counts, execution_times, initial_values):
        self.stations = {}             # Dictionary to store reservation stations
        self.instruction_queue = []    # Queue for holding instructions to be issued
        self.issue_stage_station = None  # Current station in the issue stage
        self.write_stage_station = None  # Current station in the write stage
        self.initialise_registers(initial_values)  # Initialize registers with given values
        self.create_stations(station_counts, execution_times)  # Create the reservation stations

    def initialise_registers(self, initial_values):
        # Initialize general and floating-point registers and set their initial values
        # General registers
        self.registers = {f"R{i}": Register(f"R{i}") for i in range(1, 32)}
        # Floating-point registers
        self.registers.update({f"F{i}": Register(f"F{i}", 'float', 0.0) for i in range(1, 32)})

        for value in initial_values:
            # Update register values as per the provided initial values
            register_name, new_value = value.split()
            if register_name in self.registers:
                # Determine the type of the value (int or float) and update the register
                new_value = float(new_value) if register_name.startswith('F') else int(new_value)
                self.registers[register_name].value = new_value
            else:
                print(f"Register {register_name} not found.")

    def create_stations(self, station_counts, execution_times):
        # Create reservation stations based on the given counts and execution times
        for op_type, count in station_counts.items():
            for i in range(count):
                name = f"{op_type}_{i+1}"
                self.stations[name] = ReservationStation(name, op_type, execution_times[op_type])

    def add_instruction(self, instruction):
        # Add an instruction to the queue
        self.instruction_queue.append(instruction)

    def try_issue_instruction(self):
        # Try to issue the first instruction in the queue if there are no WAW hazards
        if self.instruction_queue:
            instruction = self.instruction_queue[0]
            op_type, dest_reg, *_ = instruction.replace(',', '').split()
            write_Reg = self.registers[dest_reg]
            if write_Reg.get_write_status():
                return None  # Stall due to WAW hazard

            for name, station in self.stations.items():
                if station.op_type == op_type and not station.busy:
                    self.instruction_queue.pop(0)
                    station.load_instruction(instruction)
                    self.registers[dest_reg].set_write_status()
                    station.busy = True
                    return station
        return None

    def execute_cycle(self):
        # Execute a cycle, handling the stages of each reservation station
        # Clear the write stage station and update the register status
        if self.write_stage_station:
            self.registers[self.write_stage_station.instruction.dest].clear_write_status()
            self.write_stage_station.reset()
            self.write_stage_station = None

        start_next_issue = True
        # Handle the issue stage station
        if self.issue_stage_station:
            #Stall execution if RAW hazard
            if not self.registers[self.issue_stage_station.instruction.src1].get_write_status() and not self.registers[self.issue_stage_station.instruction.src2].get_write_status():
                self.issue_stage_station.stage = 'Execute'
                self.issue_stage_station = None
            else:
                start_next_issue = False

        # Attempt to issue an instruction if possible
        if start_next_issue:
            self.issue_stage_station = self.try_issue_instruction()

        all_stations_idle = True
        # Process each reservation station
        for name, station in self.stations.items():
            if station.instruction:
                # Handle the execute stage
                if station.stage == 'Execute':
                    if station.remaining_cycles > 1:
                        station.remaining_cycles -= 1
                    elif not self.write_stage_station:
                        station.stage = 'Write'
                        station.remaining_cycles -= 1
                        self.write_stage_station = station

                if station.stage != "Idle":
                    all_stations_idle = False

        return all_stations_idle

    def get_station_statuses(self):
        # Return the current status of each reservation station
        return {name: str(station) for name, station in self.stations.items()}

# Execution times and station counts for different instruction types
execution_times = {"ADD": 2, "MUL": 1, "DIV": 40, "STORE": 3, "BRANCH": 1}
station_counts = {"ADD": 2, "MUL": 2, "DIV": 1, "STORE": 2, "BRANCH": 1}

# Initialize the Reservation Station Manager with initial register values
initial_values = ["R1 10", "R2 11", "R3 12", "R4 13", "F2 5.4"]
rs_manager = ReservationStationManager(station_counts, execution_times, initial_values)

# List of instructions to be issued
instructions = ["ADD R1, R2, R3", "ADD R1, R2, R3", "ADD R7, R3, R3", "ADD R2, R1, R3", "MUL R4, R5, R6", "ADD R4, R8, R7"]


# Add all instructions to the manager's queue right away
for instr in instructions:
    rs_manager.add_instruction(instr)

# Simulate execution cycles
cycle = 0
while True:
    cycle += 1

    all_idle = rs_manager.execute_cycle()
    print(f"Cycle {cycle}:")
    for station, status in rs_manager.get_station_statuses().items():
        print(f"  {status} ")

    if all_idle:
        break

print("All instructions have been processed.")
