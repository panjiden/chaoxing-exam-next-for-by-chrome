def openai_chat(text, model_name='gpt-3.5-turbo'):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openaiApiKey}"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": text}]
    }
    response = requests.post(openaiEndpoint, headers=headers, json=data)

    # 检查状态码
    if response.status_code != 200:
        print(f"OpenAI API 请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return "API请求失败"

    # 新增：检查是否为空响应或非JSON
    if not response.text.strip():
        print("API 返回空响应")
        return "API返回空响应"

    # 检查是否为HTML（常见于认证失败）
    if "<html" in response.text or "<!DOCTYPE" in response.text:
        print("API 返回 HTML 页面，可能是认证失败或地址错误")
        print(f"响应内容: {response.text[:500]}...")
        return "API返回HTML页面，请检查API Key和Endpoint"

    try:
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            print("API 响应格式错误，缺少 'choices' 字段")
            print(f"响应内容: {response_data}")
            return "API响应格式错误"
    except Exception as e:
        print(f"解析JSON响应时出错: {e}")
        print(f"响应内容: {response.text}")
        return "JSON解析错误"