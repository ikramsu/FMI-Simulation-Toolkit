**PyFMI manual FMU connections**

The PyFMI GUI Application is a Python-based graphical user interface designed to facilitate the loading of Functional Mock-up Units (FMUs), manage connections between these units, and run simulations using the PyFMI library.

**Features**

Load and manage four FMUs for simulation.
Manually configure connections between FMUs. Connections are in this file for demo.
Load simulation parameters from a CSV file.
Run simulations and visualize results.
Export simulation results to a CSV file.

**Prerequisites**

Before running this script, ensure you have Anaconda installed on your system. Anaconda simplifies package management and deployment for Python projects. Visit the Anaconda website for installation instructions.

**Install packages available through conda(terminal):**

conda install conda-forge::pyfmi
conda install anaconda::numpy
conda install anaconda::pandas
conda install conda-forge::matplotlib

**Troubleshooting**

Ensure all packages are correctly installed.
Verify that the FMUs and CSV files are in the correct format and accessible to the script.

**Model connections**

connecting inputs / outputs from two models, firstsubsytem is giving the parameter as an input for the second sybsytem
connections = [(sub_system3,'Load_signal',sub_system1,'Engine.LoadSignal'),

               (sub_system1,'Engine.EngineSpeed',sub_system4,"VTMS.Coolant_Pump_Speed"),
               (sub_system1,'Engine.EngineSpeed',sub_system4,'VTMS.Engine_Speed'),
               (sub_system1,'Engine.EngineSpeed',sub_system4,'VTMS.Fan Big Speed'),
               (sub_system1,'Engine.HT ExhaustPort',sub_system4,'VTMS.HT Exhaust Port'),
               (sub_system1,'Engine.HT IntakePort',sub_system4,'VTMS.HT Intake port'),

               (sub_system1,'Engine.EngineTorque',sub_system2,'Driveline.Engine Torque'),
               (sub_system2,'Driveline.Engine Speed',sub_system1,'Engine.Speed'),
               (sub_system2,'Driveline.Start Switch',sub_system1,'Engine.StartSwitch'),

               (sub_system2,'Driveline.Vehicle Velocity',sub_system4,'VTMS.Vehicle_Velocity'),

               (sub_system3,'Brake_signal',sub_system2,'Driveline.Brake Signal'),
               (sub_system3,'Load_signal',sub_system2,'Driveline.Load Signal'),
               (sub_system2,'Driveline.Vehicle Velocity',sub_system3,'Actual_velocity')]
