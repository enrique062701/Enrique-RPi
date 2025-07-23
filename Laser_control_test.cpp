#include <iostream>
#include <string>
#include <vector>
#include <Windows.h>
#include "REMOTECONTROL.H"

int main() {
    int handle = -1;
    char devname[128] = {0};
    char regname[128] = {0};
    char id_value[256] = {0};
    int timestamp = 0;

    // Step 1: Connect to device (example: RS232 on COM3)
    const int connectiontype = 1; // RS232
    const char* port = "COM1";
    const char* csv_path = "REMOTECONTROL.csv";

    std::cout << "Connecting to device on" << port << "..." << std::endl;

    int err = rcConnect2(&handle, connectiontype, port, csv_path);
    if (err != RMTCTRLERR_OK) {
        std::cerr << "Failed to connect: " << err << std::endl;
        return 1;
    }
    std::cout << "Connected. Handle = " << handle << std::endl;

    // Step 2: Get first device name
    err = rcGetFirstDeviceName2(handle, devname, sizeof(devname));
    if (err != RMTCTRLERR_OK) {
        std::cerr << "Failed to get device name: " << err << std::endl;
        rcDisconnect2(handle);
        return 1;
    }
    std::cout << "Device name: " << devname << std::endl;

    // Step 3: Search for an ID-related register
    err = rcGetFirstRegisterName2(handle, devname, regname, sizeof(regname));
    while (err == RMTCTRLERR_OK) {
        std::string reg(regname);
        if (reg.find("ID") != std::string::npos || reg.find("id") != std::string::npos) {
            std::cout << "Found possible ID register: " << reg << std::endl;

            // Step 4: Try reading it as string
            err = rcGetRegAsString2(handle, devname, regname, id_value, sizeof(id_value), -1, &timestamp);
            if (err == RMTCTRLERR_OK) {
                std::cout << "Device ID: " << id_value << std::endl;
                break;
            } else {
                std::cerr << "Failed to read value: " << err << std::endl;
            }
        }

        err = rcGetNextRegisterName2(handle, regname, sizeof(regname));
    }

    // Step 5: Disconnect
    rcDisconnect2(handle);
    std::cout << "Disconnected." << std::endl;

    return 0;
}
