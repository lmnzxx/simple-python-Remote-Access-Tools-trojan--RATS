# simple-python-Remote-Access-Tools-trojan--RATS

### Disclaimer
**This tool is developed solely for educational purposes as part of the Computer Hacking course. The author is not responsible for any misuse or harm caused by this tool.**

This project is a Remote Access Tool (RAT) developed as part of the Computer Hacking course. It is a simple proof-of-concept tool that includes basic features such as:  
- **Screenshot capturing**  
- **Keystroke logging**  

## Current Features and Limitations  
### Features  
- Runs on **Windows operating systems**.  
- Communicates using the **socket protocol** over a local network.  

### Limitations  
- The tool is currently implemented as a Python script.  
- When compiled into a `.exe` file using `py2installer`, the file may be flagged as a virus by antivirus software.  
- Requires an open port for communication and may not work if the target system has a firewall enabled.  

## Prerequisites  
- Python 3.x installed  
- Required modules:  
  - socket
  - ImageGrab form PIL
  - keyboard from pynput
  - threading
  - ipaddress  
  - pyinstaller (if compiling to .exe)

## Contributions  
Contributions, issues, and feature requests are welcome!  
Feel free to open an issue or submit a pull request.  
