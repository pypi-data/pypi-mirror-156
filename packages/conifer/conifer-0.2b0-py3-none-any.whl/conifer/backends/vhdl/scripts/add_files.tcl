add_files ./firmware/Constants.vhd ./firmware/Types.vhd ./firmware/Tree.vhd ./firmware/AddReduce.vhd
add_files ./firmware/BDT.vhd ./firmware/BDTTop.vhd
# insert arrays

set_property FILE_TYPE {VHDL 2008} [get_files *.vhd]
set_property LIBRARY BDT [get_files *.vhd]

add_files ./firmware/SimulationInput.vhd ./firmware/SimulationOutput.vhd ./firmware/BDTTestbench.vhd