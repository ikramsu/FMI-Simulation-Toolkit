import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QInputDialog, QVBoxLayout, QWidget, QPushButton, QDialogButtonBox, QComboBox, QFileDialog, QDialog, QFormLayout, QLineEdit, QMessageBox #PyQt5 library for GUI
import numpy as np
import matplotlib.pyplot as plt
from pyfmi.fmi import load_fmu
from pyfmi import Master
import pandas as pd
import traceback

# Connection dialog
class ConnectionDialog(QDialog):
    def __init__(self, parent, connections):
        super().__init__(parent)
        self.setWindowTitle("FMU Connection")
        self.layout = QVBoxLayout()

        self.connections = connections  

        self.label1 = QLabel("Select Source FMU:")
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Sub System 1", "Sub System 2", "Sub System 3", "Sub System 4"])

        self.label2 = QLabel("Enter Source Variable:")
        self.source_variable_lineedit = QLineEdit()  

        self.label3 = QLabel("Select Target FMU:")
        self.target_combo = QComboBox()
        self.target_combo.addItems(["Sub System 1", "Sub System 2", "Sub System 3", "Sub System 4"])

        self.label4 = QLabel("Enter Target Variable:")
        self.target_variable_lineedit = QLineEdit()  

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_fmus)

        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.source_combo)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.source_variable_lineedit)
        self.layout.addWidget(self.label3)
        self.layout.addWidget(self.target_combo)
        self.layout.addWidget(self.label4)
        self.layout.addWidget(self.target_variable_lineedit)
        self.layout.addWidget(self.connect_button)

        self.setLayout(self.layout)
    
    # Map FMU name to its object in the parent class    
    def get_fmu_object(self, fmu_name):
        parent = self.parent()
        if fmu_name == "Sub System 1":
            return parent.sub_system1
        elif fmu_name == "Sub System 2":
            return parent.sub_system2
        elif fmu_name == "Sub System 3":
            return parent.sub_system3
        elif fmu_name == "Sub System 4":
            return parent.sub_system4

    def connect_fmus(self):
        # Create and add a connection based on user's input
        source_fmu = self.get_fmu_object(self.source_combo.currentText())
        source_variable = self.source_variable_lineedit.text()
        target_fmu = self.get_fmu_object(self.target_combo.currentText())
        target_variable = self.target_variable_lineedit.text()

        # Use the specific format for connections
        connection = (source_fmu, source_variable, target_fmu, target_variable)
        self.connections.append(connection)
        QMessageBox.information(self, "FMU Connection", "Connection added successfully.")

        # Print current connections and clear input fields
        print("Current Connections:")
        for connection in self.connections:
            print(connection)

        # Clear the selection and text for the next connection
        self.source_variable_lineedit.clear()
        self.target_variable_lineedit.clear()
        
class PyFMIGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyFMI GUI")
        self.setup_ui()
        self.fmus_loaded = False
        self.csv_loaded = False
        self.connections = []

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

        self.connect_fmu_button = QPushButton("Manually Connect FMUs", self)
        self.connect_fmu_button.setFixedSize(250, 60)
        self.connect_fmu_button.clicked.connect(self.show_connection_dialog)
        self.layout.addWidget(self.connect_fmu_button)

        self.run_button = QPushButton("Run PyFMI Simulation", self)
        self.run_button.setFixedSize(250, 60)
        self.run_button.clicked.connect(self.run_simulation)
        self.layout.addWidget(self.run_button)
        
        self.print_connections_button = QPushButton("Print Connections", self)
        self.print_connections_button.setFixedSize(250, 60)
        self.print_connections_button.clicked.connect(self.print_connections)
        self.layout.addWidget(self.print_connections_button)
        
    def print_connections(self):
        if self.connections:
            connection_text = "\n".join([f"{source_fmu} -> {source_variable} -> {target_fmu} -> {target_variable}"
                                     for source_fmu, source_variable, target_fmu, target_variable in self.connections])
            print("Connections:")
            print(connection_text)  
        else:
            print("No connections have been added yet.")

        
        
    def load_fmus(self):
        file_dialog = QFileDialog(self) # Open a file dialog to select FMUs
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
                
    def load_csv(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("CSV Files (*.csv)")
        
        if file_dialog.exec_():
            csv_file = file_dialog.selectedFiles()[0]
            try:
                self.input_data = pd.read_csv(csv_file) # Load the selected CSV file using pandas
                self.csv_loaded = True
                QMessageBox.information(self, "CSV Loading", "CSV file loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "CSV Loading", f"Failed to load CSV file: {str(e)}")
            
    def show_connection_dialog(self):
        dialog = ConnectionDialog(self, self.connections)  
        dialog.exec_()
        
    def run_simulation(self):
        if not self.fmus_loaded or not self.csv_loaded or not self.connections:
           QMessageBox.warning(self, "Simulation", "Please load FMUs, CSV file, and connect FMUs first.")
           return
    
        try:
            # Extract unique FMUs from the connections
            models = [self.sub_system1, self.sub_system2, self.sub_system3, self.sub_system4]

            model = Master(models, connections=self.connections)

            # Set up the simulation options
            opts = model.simulate_options()
            opts['result_handling'] = 'file'  # Store results in memory

            # Read input data from the CSV file
            Desired_velocity = self.input_data['DesiredVelocity'].values
            t_input = self.input_data['Time'].values
            u = np.transpose(np.vstack((t_input, Desired_velocity)))
            input_object = ((self.sub_system3, 'Desired_velocity'), u)

            # Simulate the FMU
            res = model.simulate(final_time= 75.0, input=input_object, options=opts)

            # Extract the results from the FMU
            time = res[self.sub_system1]['time']
            output1 = res[self.sub_system1]['Engine.FuelCons']
            output2 = res[self.sub_system3]['Desired_velocity']
            output3 = res[self.sub_system4]['VTMS.Piston Temp']

            # Save results to a CSV file
            result_df = pd.DataFrame({
                'Time': time,
                'Engine_FuelCons': output1,
                'Desired_velocity': output2,
                'VTMS_Piston Temp': output3
            })
            result_df.to_csv('FMUsimulation_results.csv', index=False)

            # Plot the results
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