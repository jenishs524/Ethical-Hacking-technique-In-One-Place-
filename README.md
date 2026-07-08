# Advanced 30-Project Security Toolkit

A Python-based interactive security toolkit designed for learning, testing, and understanding modern defensive and offensive security concepts in a controlled environment. This project brings together multiple security-focused utilities into one menu-driven program, making it easier to explore network defense, monitoring, authentication analysis, malware detection, web security, and system hardening concepts.

This repository contains two Python implementations:
- [project_menu.py](project_menu.py) – the main interactive menu-based security toolkit
- [menu_advanced.py](menu_advanced.py) – a similar advanced version with the same project structure

---

## Project Overview

This project is an educational and security-research-oriented toolkit that includes 30 security-related modules, grouped into categories such as:
- Network defense and attack detection
- DNS and ARP monitoring
- Log monitoring and alerting
- Password vaulting and secure storage concepts
- JWT analysis
- Malware scanning concepts
- Web application firewall simulation
- Session security testing
- Basic privilege escalation auditing
- SOC-style system monitoring

The tools are designed to demonstrate how security monitoring and defensive mechanisms work in practice.

---

## What This Project Does

The toolkit provides an interactive command-line menu where users can select different security tools. Each module performs a specific task, such as:
- Detecting ARP spoofing attempts
- Monitoring DNS responses for suspicious changes
- Running a simple honeypot to log connection attempts
- Auditing common privilege escalation risks
- Extracting metadata from files
- Watching system logs for suspicious authentication activity
- Checking email domains for phishing-related indicators
- Saving credentials in an encrypted local vault
- Performing subdomain discovery checks
- Detecting suspicious reverse shell processes
- Analyzing JWT token structure and payloads
- Monitoring SSH brute-force attacks
- Scanning files for known hash-based malware signatures
- Simulating a basic WAF for suspicious requests
- Testing insecure session handling behavior
- Reviewing APK permission risks
- Showing a simple AD/BloodHound-style collector concept
- Monitoring CPU, memory, and connection usage in a SOC-like dashboard

---

## Features

- Interactive menu-based interface
- 30 security-related modules
- Real-time network and system monitoring
- Logging of events to JSON files
- Simple local password vault with encryption
- Basic malware hash scanning
- Flask-based web security examples
- JWT analysis and inspection
- Network security monitoring concepts
- Educational security project structure

---

## Technologies Used

- Python 3
- subprocess
- socket
- threading
- sqlite3
- hashlib
- json
- psutil
- dnspython
- PyJWT
- Flask
- cryptography

---

## Requirements

Install the required Python libraries:

```bash
pip install dnspython psutil pyjwt cryptography flask
```

Additional system tools may be needed depending on your environment:
- tcpdump
- arping
- exiftool
- sudo access for some network and system tools

---

## Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd "Advance Project"
```

2. Install the Python dependencies:

```bash
pip install dnspython psutil pyjwt cryptography flask
```

3. Run the project:

```bash
python3 project_menu.py
```

or

```bash
python3 menu_advanced.py
```

---

## Usage

When you start the program, you will see a numbered menu with multiple security projects. Choose a number to run the corresponding tool.

Example:
- Select 1 for ARP Defender
- Select 2 for DNS Guardian
- Select 3 for Honeypot Pro
- Select 13 for Malware Scanner
- Select 14 for WAF Pro

Some tools are long-running and may require pressing Ctrl+C to stop them.

---

## Project Modules Description

### 1. ARP Defender
Detects ARP spoofing attempts by monitoring ARP traffic and comparing the gateway MAC address with the expected value.

### 2. DNS Guardian
Monitors DNS responses and checks whether a domain resolves to an unexpected IP address.

### 3. Honeypot Pro
Creates a simple multi-port honeypot that logs incoming connections and responds with basic banners.

### 4. Privilege Escalation Auditor
Collects information about the current user, sudo privileges, SUID binaries, and writable system paths.

### 5. Metadata Hunter
Scans files or directories and extracts metadata using exiftool.

### 6. Log Watcher
Monitors system logs for suspicious activity such as failed authentication attempts.

### 7. Phishing Validator
Analyzes a supplied email address by checking its domain MX records.

### 8. Vault Pro
Provides a simple encrypted password vault using Fernet encryption and SQLite storage.

### 9. Recon Pipeline
Performs basic subdomain enumeration against a target domain.

### 10. EDR Agent
Looks for suspicious processes such as reverse shells and terminates them.

### 11. JWT Breaker
Analyzes JWT tokens, inspects headers and payloads, and highlights common weaknesses.

### 12. SSH Guardian
Monitors SSH authentication logs and blocks repeated brute-force attempts using iptables.

### 13. Malware Scanner
Scans files for known malware hashes and moves suspicious files into a quarantine folder.

### 14. WAF Pro
Simulates a basic web application firewall that blocks suspicious request parameters.

### 15. Session Tester
Demonstrates insecure session handling and cookie behavior in a Flask application.

### 16. APK Ripper
Provides a basic permission-risk evaluation example for Android APK-style analysis.

### 17. AD BloodHound Collector
Shows a conceptual example of collecting Active Directory information for security analysis.

### 18. SOC Dashboard
Displays live CPU, memory, and connection information in a simple SOC-style monitoring view.

### 19–30
These are duplicate or alternate entry points that re-run modules 5–16 for easier access from the interactive menu.

---

## File Structure

```text
Advance Project/
├── project_menu.py
├── menu_advanced.py
└── README.md
```

---

## Important Notes

- This project is intended for educational, defensive, and authorized security testing purposes only.
- Some modules can interact with system-level services, network traffic, logs, or firewall rules.
- Run these tools only on systems you own or are authorized to test.
- Administrative privileges may be required for certain modules.

---

## Example Use Cases

- Learning how network monitoring tools work
- Understanding common security detection mechanisms
- Building a mini defensive security lab
- Demonstrating security concepts in classroom or training environments
- Practicing Python-based security automation

---

## Future Improvements

Possible enhancements for future versions include:
- Adding a graphical user interface (GUI)
- Improving logging and reporting
- Adding more advanced detection rules
- Supporting configuration files
- Creating a more polished dashboard
- Adding proper packaging and dependency management

---

## Conclusion

This project is a practical and interactive collection of security tools that can help users understand defensive security concepts, real-world monitoring ideas, and basic security automation using Python.

If you want, this project can also be expanded into a larger cybersecurity lab toolkit with more advanced modules and better usability.
