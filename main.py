import requests
import re
import os

# 1. 原始数据源 (指向你已有的 RSC 仓库)
RAW_URL_PREFIX = "https://raw.githubusercontent.com/Mikesuu/mikrotik/main/rsc_files/"

# 2. 映射逻辑 (根据你的 Mangle 分流习惯)
ISP_MAPPING = {
    "China_Unicom.rsc": "unicom-route",
    "China_Telecom.rsc": "telecom-route",
    "China_Mobile.rsc": "telecom-route", 
    "CERNET.rsc": "unicom-route",
    "Tencent.rsc": "telecom-route",
    "Alibaba.rsc": "unicom-route",
    "ByteDance.rsc": "unicom-route",
}

OUTPUT_DIR = "routing_rules"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_and_convert():
    # 同时匹配 IPv4 和 IPv6
    ip_pattern = re.compile(r'address=([0-9a-fA-F\.\/:]+)')
    
    for filename, table in ISP_MAPPING.items():
        print(f"📥 Processing {filename}...")
        try:
            resp = requests.get(RAW_URL_PREFIX + filename, timeout=15)
            if resp.status_code != 200: continue
            
            ips = ip_pattern.findall(resp.text)
            if not ips: continue

            # 核心：将内网放行规则与运营商规则合并
            lines = [
                f"# Full Rules for {filename} (v4/v6) - Auto Generated",
                # 导入前清理旧的内网和该 ISP 的规则，防止重复
                "/routing rule remove [find comment=\"LAN-ACCEPT\"];",
                f"/routing rule remove [find table=\"{table}\"];",
                "/delay 1s",
                # --- 置顶内网放行规则 (Order 0) ---
                f'/routing rule add dst-address=10.10.10.0/25 action=lookup-only-in-table table=main comment="LAN-ACCEPT";',
                '/routing rule add dst-address=127.0.0.1/32 action=lookup-only-in-table table=main comment="LAN-ACCEPT";',
                '/routing rule add dst-address=fe80::/10 action=lookup-only-in-table table=main comment="LAN-ACCEPT";',
            ]
            
            # --- 运营商分流规则 (IPv4 + IPv6) ---
            for ip in ips:
                lines.append(f'/routing rule add dst-address={ip} action=lookup table="{table}";')
            
            output_name = filename.replace(".rsc", "_rules.rsc")
            with open(f"{OUTPUT_DIR}/{output_name}", "w", encoding='utf-8') as f:
                f.write("\r\n".join(lines))
            print(f"✅ Success: {output_name}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_and_convert()
