**PyFMI Simulation and SSD Parsing Toolkit**

This script provides a comprehensive GUI for loading FMUs, parsing SystemStructure.ssd files, and running simulations using PyFMI and SSP standards. It includes functionalities for parsing SSD connections, organizing subsystems, and visualizing simulation results.

**Prerequisites**

Before running this script, ensure you have Anaconda installed on your system. Anaconda simplifies package management and deployment for Python projects. Visit the Anaconda website for installation instructions.

**Install packages available through conda(terminal):**

conda install conda-forge::pyfmi
conda install anaconda::numpy
conda install anaconda::pandas
conda install conda-forge::matplotlib

**Running the Script**

Navigate to script root and hit run.

**Features**

Load FMUs: Load exactly four FMUs for simulation. Demo version contains limited amount of FMUs.
Parse SSD File: Select and parse SystemStructure.ssd files to extract and organize connection data.
Run Simulations: Utilize PyFMI to simulate loaded FMUs with the specified connections and input data.
Visualize Results: Plot simulation results for analysis.

**Troubleshooting**

Ensure all packages are correctly installed.
Verify that the FMUs and CSV files are in the correct format and accessible to the script.
