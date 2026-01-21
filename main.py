import requests
import re
import os

# 1. 配置原始 RSC 数据源 (指向你已有的 mikrotik 项目)
RAW_URL_PREFIX = "https://raw.githubusercontent.com/Mikesuu/mikrotik/main/rsc_files/"

# 2. 定义映射逻辑 (基于你目前的 mangle 分流规则)
ISP_MAPPING = {
    "China_Unicom.rsc": "unicom-route",
    "China_Telecom.rsc": "telecom-route",
    "China_Mobile.rsc": "telecom-route",   # 规则14: CMCC -> Telecom
    "CERNET.rsc": "unicom-route",         # 规则15: CERNET -> Unicom
    "Tencent.rsc": "telecom-route",        # 规则16: Tencent -> Telecom
    "Alibaba.rsc": "unicom-route",         # 规则17: Alibaba -> Unicom
    "ByteDance.rsc": "unicom-route",       # 规则18: ByteDance -> Unicom
}

OUTPUT_DIR = "routing_rules"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_and_convert():
    ip_pattern = re.compile(r'address=([0-9a-fA-F\.\/:]+)')
    
    for filename, table in ISP_MAPPING.items():
        print(f"📥 Processing {filename}...")
        try:
            resp = requests.get(RAW_URL_PREFIX + filename, timeout=15)
            if resp.status_code != 200:
                continue
            
            ips = ip_pattern.findall(resp.text)
            if not ips:
                continue

            # 构建 Routing Rule 脚本
            # 先清除该表的旧规则，再添加新规则
            lines = [
                f"# Generated from {filename}",
                f"/routing rule remove [find table=\"{table}\"];",
                "/delay 1s"
            ]
            
            for ip in ips:
                # 统一使用 lookup action
                lines.append(f'/routing rule add dst-address={ip} action=lookup table="{table}";')
            
            # 保存文件
            output_name = filename.replace(".rsc", "_rules.rsc")
            with open(f"{OUTPUT_DIR}/{output_name}", "w", encoding='utf-8') as f:
                f.write("\r\n".join(lines))
            print(f"✅ Success: {output_name}")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    fetch_and_convert()
