import os
import re

# 配置参数
INPUT_DIR = "rsc_files"  # 指向你存放原始 rsc 的目录
OUTPUT_DIR = "routing_rules"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 路由表映射关系
# 逻辑：根据文件名决定流量走电信还是联通
def get_table_name(filename):
    name = filename.lower()
    if "unicom" in name:
        return "unicom-route"
    # 默认让移动、电信、大厂流量走电信
    return "telecom-route"

def convert():
    # 正则提取 address-list 中的 IP 地址段
    ip_pattern = re.compile(r'address=([0-9a-fA-F\.\/:]+)')
    
    # 遍历所有生成的 rsc 文件
    for file in os.listdir(INPUT_DIR):
        if not file.endswith(".rsc") or "_rules" in file:
            continue
        
        table_name = get_table_name(file)
        # 增加脚本头部，先清理旧规则避免重复
        new_rules = [
            f"# Generated from {file}",
            f"/routing rule remove [find table=\"{table_name}\"];",
            "/delay 1s"
        ]
        
        file_path = os.path.join(INPUT_DIR, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            ips = ip_pattern.findall(content)
            
            # 生成 Routing Rule 格式：action=lookup
            for ip in ips:
                rule_cmd = f'/routing rule add dst-address={ip} action=lookup table="{table_name}";'
                new_rules.append(rule_cmd)
        
        # 写入新的 Rules 脚本
        output_file_name = file.replace(".rsc", "_rules.rsc")
        output_path = os.path.join(OUTPUT_DIR, output_file_name)
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            f.write("\r\n".join(new_rules))
        
        print(f"✅ Converted: {file} -> {output_file_name} (Table: {table_name})")

if __name__ == "__main__":
    convert()
