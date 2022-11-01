echo "config can tool"
sudo ip link set can0 up type can bitrate 500000
sudo ip link set up can0
ip link show can0
