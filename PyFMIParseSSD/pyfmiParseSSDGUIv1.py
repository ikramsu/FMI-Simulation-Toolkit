import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox
import numpy as np
import matplotlib.pyplot as plt
from pyfmi.fmi import load_fmu
from pyfmi import Master
import pandas as pd
import traceback
import xml.etree.ElementTree as ET
import csv


"""
 This class parses the SystemStructure.ssd file of an FMU and extracts the connection data.
 It then sorts the connections by start_element and end_element, and creates subsystems from the connections.
 Finally, it replaces the start and end elements in the connections with their corresponding subsystem names.
 The script writes the new connections with subsystem names to a CSV file.
 """
class SSDParser:
    
    # Initializes the parser with the path to the SSD file and sets up empty lists for connections and subsystems.
    def __init__(self, ssd_file):
        self.ssd_file = ssd_file
        self.connections = []
        self.subsystems = {}
        self.new_connections = []

    # Parses the SSD file and extracts the connections defined within it.
    def parse_ssd_connections(self):
        tree = ET.parse(self.ssd_file)
        root = tree.getroot()
    
        self.connections = []
    
        for connection in root.iter('{http://ssp-standard.org/SSP1/SystemStructureDescription}Connection'):
            start_element = connection.get('startElement', '')
            start_connector = connection.get('startConnector', '')
            end_element = connection.get('endElement', '')
            end_connector = connection.get('endConnector', '')

            self.connections.append((start_element, start_connector, end_element, end_connector))
        
        return self.connections

    # Sorts the connections list based on the start and end elements to organize them.
    def sort_connections(self):
        self.connections = sorted(self.connections, key=lambda x: (x[0], x[2]))
        return self.connections

    # Creates a dictionary of subsystems based on the connections, assigning a unique name to each subsystem.
    def create_subsystems(self):
        self.subsystems = {}
    
        for start_element, _, end_element, _ in self.connections:
            if start_element not in self.subsystems:
                self.subsystems[start_element] = f'sub_system{len(self.subsystems) + 1}'
            
            if end_element not in self.subsystems:
                self.subsystems[end_element] = f'sub_system{len(self.subsystems) + 1}'
            
        return self.subsystems

    # Replaces the start and end elements in the connections with their corresponding subsystem names.
    def replace_elements_with_subsystems(self):
        self.new_connections = []
    
        for start_element, start_connector, end_element, end_connector in self.connections:
            start_subsystem = self.subsystems.get(start_element, start_element)
            end_subsystem = self.subsystems.get(end_element, end_element)
            self.new_connections.append((start_subsystem, start_connector, end_subsystem, end_connector))
        
        return self.new_connections

    # Writes the new connections with subsystem names to a CSV file for later use.
    def write_connections_to_csv(self, csv_file):
        with open(csv_file, 'w', newline='') as csvfile:
            fieldnames = ['start_element', 'start_connector', 'end_element', 'end_connector']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
            for connection in self.new_connections:
                writer.writerow({
                    'start_element': connection[0],
                    'start_connector': connection[1],
                    'end_element': connection[2],
                    'end_connector': connection[3]
                })

    
    

class PyFMIGUI(QMainWindow):
    
    # Sets up the main window for the GUI application.
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyFMI GUI")
        self.setup_ui()
        self.fmus_loaded = False
        self.csv_loaded = False
        self.connections = []
    
    # Sets up the user interface layout and buttons.    
    def setup_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.load_fmu_button = QPushButton("Load exactly 4 FMUs", self)
        self.load_fmu_button.setFixedSize(250, 60)
        self.load_fmu_button.clicked.connect(self.load_fmus)
        self.layout.addWidget(self.load_fmu_button)

        self.load_csv_button = QPushButton("Load speed CSV", self)
        self.load_csv_button.setFixedSize(250, 60)
        self.load_csv_button.clicked.connect(self.load_csv)
        self.layout.addWidget(self.load_csv_button)

        self.select_ssd_button = QPushButton("Select and Parse SSD", self)
        self.select_ssd_button.setFixedSize(250, 70)
        self.select_ssd_button.clicked.connect(self.load_parse_ssd)
        self.layout.addWidget(self.select_ssd_button)
        
        self.run_button = QPushButton("Run PyFMI Simulation with SSD Connections", self)
        self.run_button.setFixedSize(250, 60)
        self.run_button.clicked.connect(self.run_simulation)
        self.layout.addWidget(self.run_button)

        self.print_csv_button = QPushButton("Print model_connections.csv", self)
        self.print_csv_button.setFixedSize(250, 60)
        self.print_csv_button.clicked.connect(self.print_csv_contents)
        self.layout.addWidget(self.print_csv_button)

    # Opens a file dialog to select an SSD file and then uses SSDParser to parse it.
    def load_parse_ssd(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("SSD Files (*.ssd)")
        if file_dialog.exec_():
            ssd_file_path = file_dialog.selectedFiles()[0]
            self.parser = SSDParser(ssd_file_path)
            self.parser.parse_ssd_connections()
            self.parser.create_subsystems()
            self.parser.replace_elements_with_subsystems()
            self.parser.write_connections_to_csv('model_connections.csv')
            QMessageBox.information(self, "SSD Parsing", "SSD file parsed and model_connections.csv created successfully.")

    # Opens a file dialog to select FMU files and loads them using the pyfmi library.
    def load_fmus(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("FMU Files (*.fmu)")
        
        if file_dialog.exec_():
            fmus = file_dialog.selectedFiles()
            if len(fmus) != 4:
                QMessageBox.warning(self, "FMU Loading", "Please select exactly 4 FMU files.")
                return
            try:
                self.sub_system1 = load_fmu(fmus[0])
                self.sub_system2 = load_fmu(fmus[1])
                self.sub_system3 = load_fmu(fmus[2])
                self.sub_system4 = load_fmu(fmus[3])
                self.fmus_loaded = True
                QMessageBox.information(self, "FMU Loading", "FMUs loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "FMU Loading", f"Failed to load FMUs: {str(e)}")

    # Opens a file dialog to select a CSV file and loads it as input data.
    def load_csv(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("CSV Files (*.csv)")
        
        if file_dialog.exec_():
            csv_file = file_dialog.selectedFiles()[0]
            try:
                self.input_data = pd.read_csv(csv_file)
                self.csv_loaded = True
                QMessageBox.information(self, "CSV Loading", "CSV file loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "CSV Loading", f"Failed to load CSV file: {str(e)}")

    # Loads the connections from a CSV file and maps them to the loaded FMU objects.
    def load_connections_from_csv(self, csv_file_path):
        try:
            with open(csv_file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    start_fmu = self.get_fmu_by_name(row['start_element'])
                    end_fmu = self.get_fmu_by_name(row['end_element'])
                    if start_fmu is not None and end_fmu is not None:
                        self.connections.append((
                            start_fmu,
                            row['start_connector'],
                            end_fmu,
                            row['end_connector']
                        ))
        except Exception as e:
            QMessageBox.critical(self, "Connections Loading", f"Failed to load connections from CSV file: {str(e)}")

    # Returns an FMU object based on the provided name, using a predefined mapping.
    def get_fmu_by_name(self, fmu_name):
        fmu_mapping = {
            'Sub System 1': self.sub_system1,
            'Sub System 2': self.sub_system2,
            'Sub System 3': self.sub_system3,
            'Sub System 4': self.sub_system4
        }
        return fmu_mapping.get(fmu_name)

    # Reads and prints the contents of 'model_connections.csv' to the console.
    def print_csv_contents(self):
        try:
            with open('model_connections.csv', 'r') as file:
                print("Contents of model_connections.csv:")
                for line in file:
                    print(line.strip())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read model_connections.csv: {str(e)}")

     # Runs the simulation using the loaded FMUs and connections, along with the input data from the CSV file. It also plots the results.
    def run_simulation(self):
        if not self.fmus_loaded or not self.csv_loaded:
            QMessageBox.warning(self, "Simulation", "Please load FMUs and CSV file first.")
            return

        self.load_connections_from_csv('model_connections.csv')
        try:
            
            models = [self.sub_system1, self.sub_system2, self.sub_system3, self.sub_system4]
            model = Master(models, connections=self.connections)

            
            opts = model.simulate_options()
            opts['result_handling'] = 'file'  

            
            Desired_velocity = self.input_data['DesiredVelocity'].values
            t_input = self.input_data['Time'].values
            u = np.transpose(np.vstack((t_input, Desired_velocity)))
            input_object = ((self.sub_system3, 'Desired_velocity'), u)

            res = model.simulate(final_time=75.0, input=input_object, options=opts)

            time = res[self.sub_system1]['time']
            output1 = res[self.sub_system1]['Engine.FuelCons']
            output2 = res[self.sub_system3]['Desired_velocity']
            output3 = res[self.sub_system4]['VTMS.Piston Temp']

            
            result_df = pd.DataFrame({
                'Time': time,
                'Engine_FuelCons': output1,
                'Desired_velocity': output2,
                'VTMS_Piston Temp': output3
            })
            result_df.to_csv('FMUsimulation_results.csv', index=False)

            
            plt.figure(1)
            plt.subplot(3, 1, 1)
            plt.plot(time, output1)
            plt.ylabel("Engine_FuelCons")
            plt.xlabel("Time")

            plt.subplot(3, 1, 2)
            plt.plot(time, output2)
            plt.ylabel("Desired_velocity")
            plt.xlabel("Time")

            plt.subplot(3, 1, 3)
            plt.plot(time, output3)
            plt.ylabel("VTMS_Piston Temp")
            plt.xlabel("Time")

            plt.show()

        except Exception as e:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Simulation Error", f"Simulation failed: {str(e)}\n\n{tb}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyFMIGUI()
    window.show()
    sys.exit(app.exec_())