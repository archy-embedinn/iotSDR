# Vivado 2019.1
# iotSDR GPS Design bitfile to git repo

set origin_dir "."
set project "iotSDR_GPS_Receiver"
file delete -force $origin_dir/bitstream/$project.bit
file copy -force $origin_dir/iotSDR_GPS_pynq/iotSDR_GPS.runs/impl_1/design_1_wrapper.bit $origin_dir/bitstream/$project.bit
file copy -force $origin_dir/iotSDR_GPS_pynq/iotSDR_GPS.srcs/sources_1/bd/design_1/hw_handoff/design_1.hwh $origin_dir/bitstream/$project.hwh

set code [catch {
        file copy -force $origin_dir/iotSDR_GPS_pynq/iotSDR_GPS.runs/impl_1/design_1_wrapper.ltx $origin_dir/bitstream/$project.ltx

} result]

if {$code == 0} {
    puts "Result was $result"
} elseif {$code == 1} {
    puts "ILA is not used in the current design"
} 