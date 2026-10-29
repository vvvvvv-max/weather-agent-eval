# sft_data.py
# 注释：此文件用于存放 3 条针对「天气查询 Agent」的监督微调 (SFT) 范例数据。

SFT_DATA = [
    # 范例 1：单工具调用 (Single Tool)
    {
        "scenario": "单工具",
        "instruction": "你是一个天气查询助手，可以使用 weather(city) 和 multi_weather(cities) 工具。请根据用户问题输出JSON格式的思考和行动。",
        "input": "湛江麻章区现在的天气怎么样？",
        "output": """{
  "thought": "用户询问湛江麻章区的天气，这属于单一地点查询，我应该调用 weather 工具。",
  "action": "weather",
  "action_input": {"city": "湛江麻章"}
}"""
    },
    # 范例 2：多工具并行 (Parallel Multi-tool)
    {
        "scenario": "多工具并行",
        "instruction": "你是一个天气查询助手，可以使用 weather(city) 和 multi_weather(cities) 工具。请根据用户问题输出JSON格式的思考和行动。",
        "input": "帮我查一下湛江麻章和赤坎这两个区的天气。",
        "output": """{
  "thought": "用户一次性询问了两个地区的天气，为了提升效率，我应该使用 multi_weather 工具进行并行查询。",
  "action": "multi_weather",
  "action_input": {"cities": ["湛江麻章", "湛江赤坎"]}
}"""
    },
    # 范例 3：工具失败重试 (Tool Failure & Retry)
    {
        "scenario": "工具失败重试",
        "instruction": "你是一个天气查询助手，可以使用 weather(city) 和 multi_weather(cities) 工具。请根据用户问题输出JSON格式的思考和行动。",
        "input": "湛江麻章今天下雨吗？",
        "output": """{
  "thought": "用户询问湛江麻章的天气。我先尝试使用 weather 工具查询。",
  "action": "weather",
  "action_input": {"city": "湛江麻章"},
  "observation": "Error: City name '湛江麻章' not found in database."
}
{
  "thought": "直接输入「湛江麻章」导致工具报错，可能是数据库要求更精确的行政区划名称。我重试一次，将城市名改为「广东省湛江市麻章区」。",
  "action": "weather",
  "action_input": {"city": "广东省湛江市麻章区"}
}"""
    }
]