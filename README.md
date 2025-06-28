CS-350  Submission - Modules 5 & 6
//Module 5 - Morse Code with LEDs and LCD
This project demonstrates a Morse Code transmitter using a state machine to control LEDs representing "dots" and "dashes" and an LCD for message display. It uses GPIO pins on a Raspberry Pi to manage hardware components. Users can toggle between messages "SOS" and "OK" with a button.
//What I Did Well
I implemented a clean and responsive state machine and used threading to manage concurrent LCD and LED behavior. I also did well integrating the button press events to change the message.
//Areas to Improve
I could improve by fully completing the TODOs to automate the Morse code transmission. I also want to get better at making unit test scaffolding for embedded Python projects.
//Tools Added to Support Network
I learned to use the `gpiozero`, `adafruit_character_lcd`, and `statemachine` libraries. I also became more comfortable with hardware datasheets and GPIO pinout references.
//Transferable Skills
The project improved my comfort with state machines, threading, and GPIO; all essential for embedded or IoT development.
//Maintainability & Adaptability
I separated logic into classes and used meaningful naming, making it easy to extend this to new messages or LED patterns.


Module 6 - Final Thermostat System
The final thermostat project simulates a smart thermostat that controls heat/cool behavior based on sensor input. It features a 3-state machine (off/heat/cool), LCD readouts, buttons to control state and temperature, and UART serial output.
//What I Did Well
I integrated a temperature sensor and serial output with the hardware logic and created a clean, user-friendly display. The code structure is modular and intuitive.
//Areas to Improve
Handling edge cases (sensor read failure, button debounce) can be improved. I'd also like to explore how to log sensor data for diagnostics.
//Tools Added to Support Network
I added Adafruit’s `ahtx0` sensor library, used UART communication, and learned to manage real-time LCD data display.
//Transferable Skills
This project strengthens my embedded system skills and helps with understanding full-stack hardware-software systems.
//Maintainability & Adaptability
I used classes and threading to separate concerns, making the project easy to maintain. Additional states or sensors could be added with minimal changes.
