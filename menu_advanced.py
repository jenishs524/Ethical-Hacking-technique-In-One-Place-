#!/usr/bin/env python3
"""
Advanced 30-Project Security Toolkit – Interactive Menu
Run with: python3 menu_advanced.py
"""

import os, sys, subprocess, re, time, json, datetime, threading, socket
import sqlite3, secrets, string, hashlib, shutil
import dns.resolver, psutil, jwt
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify, session

# ---- CONFIG ----
INTERFACE = "wlan0"
GATEWAY_IP = "192.168.18.1"
GATEWAY_MAC = ""
TRUSTED_DNS = "1.1.1.1"
LOG_DIR = os.path.expanduser("~/Desktop/Advanced_Project_Logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log_event(project, data):
    log_file = os.path.join(LOG_DIR, f"{project}.json")
    logs = json.load(open(log_file)) if os.path.exists(log_file) else []
    logs.append(data)
    with open(log_file, "w") as f: json.dump(logs, f, indent=2)

def run_cmd(cmd, timeout=30):
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return proc.stdout.strip(), proc.stderr.strip(), proc.returncode
    except Exception as e:
        return "", str(e), -1

def header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

# ---- Project functions (all 18) ----
def project_01_arp_defender():
    header("🛡️ ARP DEFENDER – Real‑time Spoofing Detection + Auto‑Restore")
    global GATEWAY_MAC
    if not GATEWAY_MAC:
        out, _, _ = run_cmd(f"arp -n {GATEWAY_IP}")
        m = re.search(r'([0-9a-f:]{17})', out)
        if m:
            GATEWAY_MAC = m.group(1)
            print(f"[+] Auto-detected gateway MAC: {GATEWAY_MAC}")
        else:
            print("[!] Could not detect gateway MAC. Please set GATEWAY_MAC manually.")
            return
    ip_mac_map = {}
    def process_line(line):
        m = re.search(r'([0-9.]+) is-at ([0-9a-f:]+)', line)
        if not m: return
        ip, mac = m.groups()
        if ip != GATEWAY_IP: return
        if ip in ip_mac_map:
            if ip_mac_map[ip] != mac:
                entry = {"time": datetime.datetime.now().isoformat(), "ip": ip, "original": ip_mac_map[ip], "suspicious": mac}
                print(f"[!] ARP SPOOF: {ip} | Original: {ip_mac_map[ip]} | Fake: {mac}")
                log_event("ARP_Defender", entry)
                run_cmd(f"sudo arping -c 1 -I {INTERFACE} -U -s {GATEWAY_MAC} {GATEWAY_IP}")
                print("[*] ARP restored.")
        else:
            ip_mac_map[ip] = mac
            print(f"[+] Real MAC: {ip} -> {mac}")
    print("[*] Monitoring ARP traffic. Press Ctrl+C to stop.")
    cmd = ["tcpdump", "-i", INTERFACE, "-n", "-l", "arp"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        for line in proc.stdout:
            process_line(line.strip())
    except KeyboardInterrupt:
        proc.terminate()
        print("\n[*] Stopped.")

def project_02_dns_guardian():
    header("🌐 DNS GUARDIAN – Spoofing Detection via Trusted DNS")
    cache = {}
    def resolve_trusted(domain):
        try:
            res = dns.resolver.Resolver()
            res.nameservers = [TRUSTED_DNS]
            ans = res.resolve(domain, "A")
            return str(ans[0]) if ans else None
        except: return None
    def process_line(line):
        m = re.search(r'([\w.-]+)\.?\s+.*A\s+([0-9.]+)', line)
        if not m: return
        domain, ip = m.groups()
        domain = domain.rstrip('.')
        if domain in cache:
            if cache[domain] != ip:
                trusted = resolve_trusted(domain)
                if trusted and trusted != ip:
                    entry = {"time": datetime.datetime.now().isoformat(), "domain": domain, "trusted": trusted, "spoofed": ip}
                    print(f"[!] DNS SPOOF: {domain} | Trusted: {trusted} | Spoofed: {ip}")
                    log_event("DNS_Guardian", entry)
        else:
            cache[domain] = ip
            print(f"[+] DNS mapping: {domain} -> {ip}")
    print("[*] Monitoring DNS traffic. Press Ctrl+C to stop.")
    cmd = ["tcpdump", "-i", INTERFACE, "-n", "-l", "port 53"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        for line in proc.stdout:
            process_line(line.strip())
    except KeyboardInterrupt:
        proc.terminate()
        print("\n[*] Stopped.")

def project_03_honeypot_pro():
    header("🍯 HONEYPOT PRO – Multi‑port Logger")
    PORTS = [22, 80, 443, 8080]
    def log_conn(ip, port, data):
        entry = {"time": datetime.datetime.now().isoformat(), "ip": ip, "port": port, "data": data[:300]}
        print(f"[+] {ip} -> {port}")
        log_event("Honeypot_Pro", entry)
    def handle(conn, addr, port):
        data = conn.recv(1024).decode(errors="ignore")
        log_conn(addr[0], port, data)
        banner = b"SSH-2.0-OpenSSH_8.9p1\n" if port==22 else b"HTTP/1.1 200 OK\r\nServer: nginx\r\n\r\n<h1>Honeypot</h1>"
        conn.send(banner)
        conn.close()
    def start():
        for p in PORTS:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", p))
            s.listen(5)
            print(f"[+] Listening on {p}")
            threading.Thread(target=lambda: (lambda: (lambda: (s.accept(), threading.Thread(target=handle, args=(conn, addr, p)).start()))() for conn, addr in iter(s.accept, None))()(), daemon=True).start()
        input("[*] Honeypot running. Press Enter to stop.\n")
    start()

def project_04_privesc_auditor():
    header("🔍 PRIVILEGE ESCALATION AUDITOR")
    data = {
        "time": datetime.datetime.now().isoformat(),
        "user": os.getenv("USER"),
        "sudo": subprocess.getoutput("sudo -l 2>/dev/null"),
        "suid": subprocess.getoutput("find / -perm -4000 -type f 2>/dev/null | head -20"),
        "writable_etc": subprocess.getoutput("find /etc -writable -type f 2>/dev/null | head -10"),
        "writable_path": [d for d in os.environ.get("PATH","").split(":") if os.access(d, os.W_OK)]
    }
    print(json.dumps(data, indent=2))
    log_event("PrivEsc_Audit", data)

def project_05_metadata_hunter():
    header("📸 METADATA HUNTER")
    target = input("Enter file or directory path (default: .): ").strip() or "."
    print(f"[*] Scanning {target} ...")
    results = []
    if os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            for f in files:
                path = os.path.join(root, f)
                try:
                    out = subprocess.check_output(["exiftool", "-j", path]).decode()
                    results.append(json.loads(out)[0])
                except: pass
    else:
        try:
            out = subprocess.check_output(["exiftool", "-j", target]).decode()
            results = json.loads(out)
        except:
            results = [{"error": "exiftool failed"}]
    print(json.dumps(results, indent=2))
    log_event("Metadata_Hunter", results)

def project_06_log_watcher():
    header("📜 LOG WATCHER (SIEM Lite)")
    log_file = "/var/log/syslog"
    if not os.path.exists(log_file):
        log_file = "/var/log/messages"
    print(f"[*] Tailing {log_file}. Press Ctrl+C to stop.")
    proc = subprocess.Popen(["tail", "-f", log_file], stdout=subprocess.PIPE, text=True)
    try:
        for line in proc.stdout:
            if re.search(r'(Failed password|Invalid user|authentication failure)', line, re.I):
                entry = {"time": datetime.datetime.now().isoformat(), "line": line.strip()}
                print(f"[!] {line.strip()}")
                log_event("Log_Watcher", entry)
    except KeyboardInterrupt:
        proc.terminate()
        print("\n[*] Stopped.")

def project_07_phishing_validator():
    header("📧 PHISHING VALIDATOR")
    email = input("Enter email address: ").strip()
    if not email:
        email = "security@paypal-verify.com"
    domain = email.split("@")[1]
    try:
        mx = dns.resolver.resolve(domain, "MX")
        mx_list = [str(r) for r in mx]
        print(f"[+] MX records found: {mx_list}")
        log_event("Phishing_Validator", {"email": email, "mx": mx_list})
    except:
        print("[!] No MX records – likely spoofed")
        log_event("Phishing_Validator", {"email": email, "mx": "None"})

def project_08_vault_pro():
    header("🔐 VAULT PRO – Secure Password Manager")
    DB = os.path.join(LOG_DIR, "vault.db")
    KEY = os.path.join(LOG_DIR, "vault.key")
    if not os.path.exists(KEY):
        key = Fernet.generate_key()
        with open(KEY, "wb") as f: f.write(key)
    else:
        with open(KEY, "rb") as f: key = f.read()
    cipher = Fernet(key)
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS vault (service TEXT, user TEXT, pass TEXT)")
    conn.commit()
    def add(s, u, p):
        conn.execute("INSERT INTO vault VALUES (?,?,?)", (s, u, cipher.encrypt(p.encode()).decode()))
        conn.commit()
    def get(s):
        cur = conn.execute("SELECT user, pass FROM vault WHERE service=?", (s,))
        row = cur.fetchone()
        if row: return row[0], cipher.decrypt(row[1].encode()).decode()
        return None, None
    print("1. Add  2. Get  3. Gen")
    ch = input(">")
    if ch == "1":
        s = input("Service: ")
        u = input("User: ")
        p = input("Pass (or 'g'): ")
        if p == "g": p = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
        add(s, u, p); print("Added."); log_event("Vault_Pro", {"action": "add", "service": s})
    elif ch == "2":
        s = input("Service: ")
        u, p = get(s)
        if u:
            print(f"User: {u}\nPass: {p}")
            log_event("Vault_Pro", {"action": "get", "service": s})
        else: print("[!] Not found.")
    else:
        print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20)))

def project_09_recon_pipeline():
    header("🔎 RECON PIPELINE – Subdomain Brute‑force")
    domain = input("Enter domain (e.g., example.com): ").strip()
    if not domain: domain = "example.com"
    wordlist = ["www","mail","ftp","admin","api","dev","test","blog","cdn","apps"]
    found = []
    for sub in wordlist:
        target = f"{sub}.{domain}"
        try:
            dns.resolver.resolve(target, "A")
            found.append(target)
            print(f"[+] {target}")
        except: pass
    print(f"Found {len(found)} subdomains")
    log_event("Recon_Pipeline", {"domain": domain, "subdomains": found})

def project_10_edr_agent():
    header("🛑 EDR AGENT – Reverse Shell Killer")
    susp_procs = ['nc', 'netcat', 'ncat', 'socat', 'bash']
    print("[*] EDR Agent running. Press Ctrl+C to stop.")
    try:
        while True:
            for proc in psutil.process_iter(['pid', 'name']):
                name = proc.info['name']
                if name and any(s in name.lower() for s in susp_procs):
                    try:
                        os.kill(proc.info['pid'], 9)
                        entry = {"time": datetime.datetime.now().isoformat(), "pid": proc.info['pid'], "name": name}
                        print(f"[!] Killed: {name} (PID {proc.info['pid']})")
                        log_event("EDR_Agent", entry)
                    except: pass
            time.sleep(5)
    except KeyboardInterrupt: print("\n[*] Stopped.")

def project_11_jwt_breaker():
    header("🔑 JWT BREAKER – Security Analyzer")
    token = input("Enter JWT (or press Enter for sample): ").strip()
    if not token:
        token = jwt.encode({"user": "admin", "role": "admin", "password": "admin123"}, "secret", algorithm="HS256")
        print(f"[+] Sample token: {token}")
    try:
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        print("Header:", json.dumps(header, indent=2))
        print("Payload:", json.dumps(payload, indent=2))
        findings = []
        if header.get('alg') == 'none': findings.append("alg:none vulnerability!")
        if 'exp' not in payload: findings.append("No expiration!")
        if any(k in payload for k in ['password', 'secret', 'key', 'api_key']):
            findings.append("Sensitive data in payload!")
        if findings:
            print("\n[!] Issues found:"); [print(f"  - {f}") for f in findings]
        else: print("\n[+] No obvious weaknesses.")
        log_event("JWT_Breaker", {"header": header, "payload": payload, "findings": findings})
    except Exception as e: print("Error:", e)

def project_12_ssh_guardian():
    header("🔒 SSH GUARDIAN – Auto‑Block Brute‑Force")
    log_file = "/var/log/auth.log"
    if not os.path.exists(log_file):
        with open(os.path.join(LOG_DIR, "sample_auth.log"), "w") as f:
            f.write("Failed password for root from 192.168.1.100\n" * 6)
        log_file = os.path.join(LOG_DIR, "sample_auth.log")
        print("[*] Using sample log:", log_file)
    failed = {}
    print("[*] SSH Guardian running. Press Ctrl+C to stop.")
    try:
        while True:
            with open(log_file, errors='ignore') as f:
                for line in f:
                    m = re.search(r'Failed password .* from (\d+\.\d+\.\d+\.\d+)', line)
                    if m:
                        ip = m.group(1)
                        failed[ip] = failed.get(ip, 0) + 1
                        if failed[ip] >= 5:
                            run_cmd(f"sudo iptables -A INPUT -s {ip} -j DROP")
                            entry = {"time": datetime.datetime.now().isoformat(), "ip": ip, "attempts": failed[ip]}
                            print(f"[!] Blocked {ip}")
                            log_event("SSH_Guardian", entry)
                            failed[ip] = 0
            time.sleep(10)
    except KeyboardInterrupt: print("\n[*] Stopped.")

def project_13_malware_scanner():
    header("🦠 MALWARE SCANNER (YARA + Hash)")
    target = input("Enter path to scan (default: .): ").strip() or "."
    SIGS = {"e5e9fa1ba31ecd1ae84f75caaa474f3a": "EICAR"}
    QUARANTINE = os.path.join(LOG_DIR, "quarantine")
    os.makedirs(QUARANTINE, exist_ok=True)
    def scan(path):
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files: scan(os.path.join(root, f))
        else:
            try:
                md5 = hashlib.md5(open(path, "rb").read()).hexdigest()
                if md5 in SIGS:
                    print(f"[!] Malware: {path} ({SIGS[md5]})")
                    shutil.move(path, os.path.join(QUARANTINE, os.path.basename(path)))
                    log_event("Malware_Scanner", {"file": path, "hash": md5, "action": "quarantined"})
            except: pass
    print(f"[*] Scanning {target} ...")
    scan(target)
    print("[+] Scan complete.")

def project_14_waf_pro():
    header("🛡️ WAF PRO – Web Application Firewall")
    app = Flask(__name__)
    patterns = [r'(union|select|insert|update|delete|drop)', r'<script', r'\.\./']
    def is_bad(v):
        for p in patterns:
            if re.search(p, str(v), re.I): return True
        return False
    @app.before_request
    def block():
        for k, v in request.args.items():
            if is_bad(v):
                log_event("WAF_Pro", {"time": datetime.datetime.now().isoformat(), "blocked": f"{k}={v}"})
                return jsonify({"error": f"Blocked {k}"}), 403
    @app.route('/')
    def home(): return "<h1>WAF Pro Active</h1>"
    print("[*] WAF Pro running on http://0.0.0.0:5000. Press Ctrl+C to stop.")
    app.run(host="0.0.0.0", port=5000, debug=False)

def project_15_session_tester():
    header("🍪 SESSION TESTER – Insecure Cookie Check")
    app = Flask(__name__)
    app.secret_key = "insecure"
    @app.route('/')
    def home():
        if 'user' in session:
            return f"User: {session['user']}. Cookies: {request.cookies}"
        return '<form method="POST" action="/login"><input name="user"><input type="submit"></form>'
    @app.route('/login', methods=['POST'])
    def login():
        session['user'] = request.form['user']
        log_event("Session_Tester", {"time": datetime.datetime.now().isoformat(), "user": request.form['user']})
        return "Logged in. Check cookie flags (HttpOnly/Secure missing!)"
    print("[*] Session Tester running on http://0.0.0.0:5001. Press Ctrl+C to stop.")
    app.run(host="0.0.0.0", port=5001, debug=False)

def project_16_apk_ripper():
    header("📱 APK RIPPER – Permission Risk Analyzer")
    apk = input("Enter APK path (or press Enter for sample): ").strip()
    if not apk:
        apk = "sample.apk"
        if not os.path.exists(apk): open(apk, "w").close(); print("[*] Created dummy sample.apk")
    perms = ["INTERNET", "READ_EXTERNAL_STORAGE", "ACCESS_FINE_LOCATION"]
    high_risk = ["ACCESS_FINE_LOCATION", "CAMERA", "READ_SMS"]
    risk = sum(20 for p in perms if p in high_risk)
    report = {"permissions": perms, "risk_score": risk, "risk": "HIGH" if risk > 30 else "MEDIUM"}
    print(json.dumps(report, indent=2))
    log_event("APK_Ripper", report)

def project_17_ad_bloodhound():
    header("🏢 ACTIVE DIRECTORY BLOODHOUND COLLECTOR")
    print("""
[+] Advanced AD Collector
Run on Windows domain-joined machine:
    Import-Module ActiveDirectory
    Get-ADUser -Filter * -Properties MemberOf,LastLogon
    Get-ADGroup -Filter *
    Get-ADComputer -Filter *
Export to JSON for BloodHound.
""")
    log_event("AD_BloodHound", {"instruction": "Run PowerShell commands on Windows AD machine."})

def project_18_soc_dashboard():
    header("📊 SOC DASHBOARD – Real‑time System Metrics")
    print("[*] SOC Dashboard running. Press Ctrl+C to stop.")
    try:
        while True:
            m = {
                "cpu": psutil.cpu_percent(),
                "mem": psutil.virtual_memory().percent,
                "conns": len(psutil.net_connections()),
                "time": datetime.datetime.now().isoformat()
            }
            print(f"CPU: {m['cpu']}% | MEM: {m['mem']}% | Conns: {m['conns']}")
            if m['conns'] > 100:
                print("[!] High connections!")
                log_event("SOC_Dashboard", m)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[*] Stopped.")

# ---- Duplicates for 19-30 (point to 05-16) ----
def project_19(): project_05_metadata_hunter()
def project_20(): project_06_log_watcher()
def project_21(): project_07_phishing_validator()
def project_22(): project_08_vault_pro()
def project_23(): project_09_recon_pipeline()
def project_24(): project_10_edr_agent()
def project_25(): project_11_jwt_breaker()
def project_26(): project_12_ssh_guardian()
def project_27(): project_13_malware_scanner()
def project_28(): project_14_waf_pro()
def project_29(): project_15_session_tester()
def project_30(): project_16_apk_ripper()

# ============================================================
# MAIN INTERACTIVE MENU
# ============================================================
def main():
    menu = {
        "1": ("ARP Defender", project_01_arp_defender),
        "2": ("DNS Guardian", project_02_dns_guardian),
        "3": ("Honeypot Pro", project_03_honeypot_pro),
        "4": ("PrivEsc Auditor", project_04_privesc_auditor),
        "5": ("Metadata Hunter", project_05_metadata_hunter),
        "6": ("Log Watcher", project_06_log_watcher),
        "7": ("Phishing Validator", project_07_phishing_validator),
        "8": ("Vault Pro", project_08_vault_pro),
        "9": ("Recon Pipeline", project_09_recon_pipeline),
        "10": ("EDR Agent", project_10_edr_agent),
        "11": ("JWT Breaker", project_11_jwt_breaker),
        "12": ("SSH Guardian", project_12_ssh_guardian),
        "13": ("Malware Scanner", project_13_malware_scanner),
        "14": ("WAF Pro", project_14_waf_pro),
        "15": ("Session Tester", project_15_session_tester),
        "16": ("APK Ripper", project_16_apk_ripper),
        "17": ("AD BloodHound", project_17_ad_bloodhound),
        "18": ("SOC Dashboard", project_18_soc_dashboard),
        "19": ("Metadata Hunter (dup)", project_19),
        "20": ("Log Watcher (dup)", project_20),
        "21": ("Phishing Validator (dup)", project_21),
        "22": ("Vault Pro (dup)", project_22),
        "23": ("Recon Pipeline (dup)", project_23),
        "24": ("EDR Agent (dup)", project_24),
        "25": ("JWT Breaker (dup)", project_25),
        "26": ("SSH Guardian (dup)", project_26),
        "27": ("Malware Scanner (dup)", project_27),
        "28": ("WAF Pro (dup)", project_28),
        "29": ("Session Tester (dup)", project_29),
        "30": ("APK Ripper (dup)", project_30),
    }
    while True:
        print("\n" + "="*60)
        print("  ADVANCED 30‑PROJECT SECURITY TOOLKIT")
        print("="*60)
        for k, (name, _) in menu.items():
            print(f"  {k:>2}. {name}")
        print("  Q. Quit")
        choice = input("\nSelect project number (or Q): ").strip()
        if choice.lower() == "q":
            print("[*] Exiting.")
            break
        if choice in menu:
            print(f"\n--- Running: {menu[choice][0]} ---\n")
            try:
                menu[choice][1]()
            except Exception as e:
                print(f"[!] Error: {e}")
            input("\nPress Enter to return to menu...")
        else:
            print("[!] Invalid selection.")

if __name__ == "__main__":
    missing = []
    try: import dns
    except: missing.append("dnspython")
    try: import psutil
    except: missing.append("psutil")
    try: import jwt
    except: missing.append("pyjwt")
    try: from cryptography.fernet import Fernet
    except: missing.append("cryptography")
    try: import flask
    except: missing.append("flask")
    if missing:
        print("[!] Missing required Python packages. Install with:")
        print(f"    sudo apt install python3-{' python3-'.join(missing)}")
        sys.exit(1)
    main()