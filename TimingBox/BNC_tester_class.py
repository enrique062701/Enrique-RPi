import epics
import unittest
import time
import numpy as np


class BNC_Tester(unittest.TestCase):
    def __init__(self, USER: str, channels: int, **kwargs):
        self.USER = USER
        self.channels = channels

    def PV_setup(self):
        """
        This will initialize all the PV variables that will be tested.
        The dictionaries will now look like:
        Delay_PVs = { 1: EPICS PV }
        """
        pv_map = {
            "Delay" : "Delay_PVs",
            "Width" : "Width_PVs",
        }

        pv_rbv_map = {
            "Delay_RBV" : "Delay_PVs_RBV",
            "Width_RBV" : "Width_PVs_RBV",
        }
        self.Delay_PVs = {} # Will store the PVs in the dictionary.
        self.Delay_PVs_RBV = {}
        self.Width_PVs = {}
        self.Width_PVs_RBV = {}


        for i in range(self.channels):
            for pv_name, pv_dict_name in pv_map.items():
                dict_name = pv_map[pv_name]
                pv_dict = getattr(self, dict_name)

                pv_dict[i] = epics.PV(f"{self.USER}Ch{i}:{pv_name}")
                pv_dict[i].connect(timeout=5)

            for pv_name, pv_dict_name in pv_rbv_map.items():
                dict_name = pv_rbv_map[pv_name]
                pv_dict = getattr(self, dict_name)

                pv_dict[i] = epics.PV(f"{self.USER}Ch{i}:{pv_name}")
                pv_dict[i].connect(timeout = 5)
            print(f"Finished channel {i}.")



    def test_delays(self):
        """
        This function will feed values into the EPICS streamline. It will check if the values are equal.
        """
        rbv_dict = {
            "Delay" : "Delay_RBV",
            "Width" : "Width_RBV",
        }

        delays = np.linspace(0, 0.01, 0.001)
        width = np.linspace(0.001, 0.1, 0.001)

        # We know that the PV are name as USER:Ch1:Delay and USER:Ch1:Delay_RBV so to get RBV can do 

        for channels, pv_variable in self.Delay_PVs.items():
            for i in range(len(delays)):
                self.Delay_PVs[channels].put(i)
                time.sleep(0.02)
                rbv = epics.caget(f"{self.Delay_PVs[channels]}_RBV")
                self.assertEqual(rbv, delays(i)) # This will check if the RBV is the same as the inputted value.





    
if __name__ == "__main__":
    pass



