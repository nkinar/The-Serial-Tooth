# The Serial Tooth

*A Bluetooth LE serial port communicator program written in Python*

## What is it?

 A Bluetooth LE module (such as the BLE121) can be set up as a virtual serial port.
 This simple Python program will communicate with the Bluetooth LE module using a
 USB dongle based on the BLED112 and Bluegiga's BGAPI.

![Photo](serial-tooth.png)

## Hardware Dependencies

* BLED112 Bluetooth Dongle

## Code Dependencies

* Python 3
* pygatt library
* tkinter

# Getting Started

Install pygatt using `pip`:

```
pip3 install pygatt
```

In the `bt-terminal-gui.py` code, change the `CHARACTERISTIC_ADDR` to whatever
is required to match the address set by the code running on the Bluetooth LE module.
An example is shown below.  

```
CHARACTERISTIC_ADDR = 'e7add780-b042-4876-aae1-112855353cc1'
```

Then, to start the Python program,
```
python3 bt-terminal-gui.py
```

Note that `python3` is the name of your Python interpreter and this name
can change on different systems.

Other considerations:

* The Quit button quits the program.
* The Clear button clears the terminal.
* The Connect button connects to the device.
* The Device Address is the Bluetooth LE device address.  This address can
be obtained from:

  * Microsoft Bluetooth LE Explorer app for Windows
  * Bluetility https://github.com/jnross/Bluetility for Mac OS X
  * `hcitool lescan` using `hcitool` for GNU/Linux

## Built With

* Python 3

## Credits

* Terminal Interfaces in Python for commander.py: http://zderadicka.eu/terminal-interfaces-in-python/
* https://github.com/izderadicka/xmpp-tester/blob/master/commander.py

## Built @

* Smart Water Systems Lab (University of Saskatchewan)

## Author

* **Nicholas J. Kinar** - code for bt-terminal-gui.py

## License

This project is licensed under the MIT license - see the [LICENSE.md](LICENSE.md) file for details.
