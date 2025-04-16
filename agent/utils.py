import json

def parse_llm_response(response):
  """解析 LLM 回應，支援 AIMessage、str 或 dict"""
  if hasattr(response, 'content'):
    return json.loads(response.content)
  elif isinstance(response, str):
    return json.loads(response)
  elif isinstance(response, dict):
    return response
  else:
    raise ValueError(f"無法解析的回應類型：{type(response)}")