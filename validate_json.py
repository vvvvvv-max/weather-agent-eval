# validate_json.py
# 注释：此脚本用于验证 LLM 输出的文字是否符合 JSON 格式规范（对应进阶加分项）。

import json
import re
import subprocess

def check_json_compliance(llm_output: str):
    """
    验证输出是否合规。
    步骤：
    1. 尝试使用正规表达式提取 JSON 区块（防止模型输出 markdown 标记如 ```json）。
    2. 使用题目要求的 python -c 指令进行严格验证。
    """
    try:
        # 提取文本中的 JSON 区块
        json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if not json_match:
            return False, "未找到 JSON 结构"
        
        json_str = json_match.group(0)
        
        # 将字符串安全转义，以便在命令行中执行
        # 替换掉可能引发命令行解析错误的双引号
        safe_json_str = json_str.replace('"', '\\"').replace('\n', ' ')
        
        # 使用题目要求的指令进行验证
        command = f'python -c "import json; json.loads(\'{safe_json_str}\')"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 进一步检查关键字段是否齐全
            data = json.loads(json_str)
            required_keys = ["thought", "action", "action_input"]
            if all(key in data for key in required_keys):
                return True, "JSON 格式合规，且包含所需字段"
            else:
                return False, "JSON 格式合规，但缺少必要字段"
        else:
            return False, f"JSON 解析错误: {result.stderr.strip()}"
            
    except Exception as e:
        return False, f"验证过程发生异常: {str(e)}"

# 测试用代码
if __name__ == "__main__":
    # 模拟 L1 的输出（通常夹带多余文字，容易违规）
    output_L1 = '好的，我来帮您查询。\n{"thought": "查询麻章天气", "action": "weather", "action_input": {"city": "湛江麻章"}}'
    
    # 模拟 L2 的输出（格式纯净）
    output_L2 = '{"thought": "查询麻章天气", "action": "weather", "action_input": {"city": "湛江麻章"}}'
    
    print(f"L1 验证结果: {check_json_compliance(output_L1)}")
    print(f"L2 验证结果: {check_json_compliance(output_L2)}")