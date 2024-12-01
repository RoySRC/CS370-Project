# Raspberry PI GPU Auto-Overclocker
The goal of this project is to develop a raspberry PI GPU auto overclocker and evaluate the results against two criterions: cost and marketability of the PI overclocker, and power consumption of the overclocked GPU. There are third party vendor overclocking utilities such as MSI Afterburner and EVGA Precision X1. The problem with these libraries is that they are only designed to work on Windows Operating Systems. These libraries use the OC Scanner algorithm to automatically overclock (OC) a GPU. The OC Scanner algorithm sets both the frequency and voltage for overclocking. NVIDIA does not allow Linux to modify the core voltage of their GPUs, instead Linux can only modify core and memory frequency. Therefore we have developed our own auto overclocking algorithm which resides in the Raspberry PI. In this paper we discuss our proposed solution and show that our solution is energy efficient and does not increase the power consumption of an overclocked GPU unlike the OC Scanner algorithm. In this paper we also evaluate the cost and marketability of the project.

[Paper](https://github.com/RoySRC/CS370-Project/blob/main/Final_Paper.pdf)
