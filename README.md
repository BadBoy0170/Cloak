# Cloak - Python Backdoor Framework

Cloak is an intelligent Python backdoor injector that generates payloads via msfvenom and seamlessly injects them into target Python scripts while evading basic detection.

## Features

- Generates Python meterpreter payloads
- Intelligently splits payload into multiple parts
- Injects payload into existing Python scripts
- Optional root execution requirement
- GitHub repository injection support
- Cross-version Python compatibility (Python 2 & 3)

## Installation

1. Ensure you have `msfvenom` installed (part of Metasploit Framework)
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/cloak.git
   cd cloak
   ```

## Usage

```bash
python cloak.py
```

Follow the interactive prompts to:

- Specify target (GitHub repo or local file)
- Set LHOST/LPORT (defaults to detected IP and port 443)
- Choose whether to require root execution

## Requirements

- Linux (recommended)
- Python 2.7 or 3.x
- msfvenom (Metasploit Framework)

## Compatibility

Tested on:

- Kali Linux
- Ubuntu
- Other Debian-based distributions

## Disclaimer

This tool is for educational and authorized penetration testing purposes only. The developers assume no liability and are not responsible for any misuse or damage caused by this program.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.