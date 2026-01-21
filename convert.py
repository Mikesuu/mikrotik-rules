import requests
import re
import os

# 配置：请修改为你存放 RSC 文件的 GitHub 仓库地址
RAW_URL_PREFIX = "https://raw.githubusercontent.com/Mikesuu/mikrotik/main/rsc_files/"
# 需要转换的文件列表
FILES = ["China_Telecom.rsc", "China_Unicom.rsc", "China_Mobile.rsc", "Tencent.rsc", "Alibaba.rsc"]

OUTPUT_DIR = "routing_rules"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_table(filename):
    if "Unicom" in filename: return "unicom-route"
    if "Telecom" in filename: return "telecom-route"
    return "telecom-route" # 其他默认走电信

def run():
    ip_pattern = re.compile(r'address=([0-9a-fA-F\.\/:]+)')
    
    for file in FILES:
        print(f"📥 Fetching {file}...")
        resp = requests.get(RAW_URL_PREFIX + file)
        if resp.status_code != 200: continue
        
        table = get_table(file)
        ips = ip_pattern.findall(resp.text)
        
        # 构建 ROS 脚本内容
        lines = [f"/routing rule remove [find table=\"{table}\"];", "/delay 1s"]
        for ip in ips:
            lines.append(f'/routing rule add dst-address={ip} action=lookup table="{table}";')
        
        with open(f"{OUTPUT_DIR}/{file.replace('.rsc', '_rules.rsc')}", "w") as f:
            f.write("\r\n".join(lines))
        print(f"✅ Created rules for {file}")

if __name__ == "__main__":
    run()
