import requests
import re
import os

RAW_URL_PREFIX = "https://raw.githubusercontent.com/Mikesuu/mikrotik/main/rsc_files/"
ISP_MAPPING = {
    "China_Unicom.rsc": "unicom",
    "China_Telecom.rsc": "telecom",
    "China_Mobile.rsc": "telecom", 
    "CERNET.rsc": "unicom",
    "Tencent.rsc": "telecom",
    "Alibaba.rsc": "unicom",
    "ByteDance.rsc": "unicom",
}
OUTPUT_DIR = "routing_rules"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_and_convert():
    ip_pattern = re.compile(r'address=([0-9a-fA-F\.\/:]+)')
    for filename, table in ISP_MAPPING.items():
        try:
            resp = requests.get(RAW_URL_PREFIX + filename, timeout=15)
            if resp.status_code == 200:
                ips = ip_pattern.findall(resp.text)
                if ips:
                    lines = [f"/routing rule remove [find table=\"{table}\" and comment!=\"STATIC-MARK-MAPPING\"];"]
                    for ip in ips:
                        lines.append(f'/routing rule add dst-address={ip} action=lookup table="{table}";')
                    output_name = filename.replace(".rsc", "_rules.rsc")
                    with open(f"{OUTPUT_DIR}/{output_name}", "w", encoding='utf-8') as f:
                        f.write("\r\n".join(lines))
        except:
            pass

if __name__ == "__main__":
    fetch_and_convert()
