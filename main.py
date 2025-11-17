import argparse
import json
import sys
import time
import os
import re
import urllib.parse

import dashscope
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
import requests

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True, errors='ignore')

# 新增OpenAI相关变量
openaiApiKey = "sk-kqibuzjqfmdzwgukixolsxvmolsiyrdkaxbvvalhpyxaggwr"
openaiEndpoint = "https://api.siliconflow.com/v1/chat/completions"
model_name = "Qwen/Qwen3-VL-32B-Instruct"  # 新增: 模型名称变量

arg = sys.argv
if len(arg) < 2:
    username = input('请输入超星账号:')
    password = input('请输入超星密码:')
    url = input('请输入进入考试页面后的网址:')
    model = input("答案获取方式：1.本地ollama 2.通义千问 3.OpenAI兼容服务")

    modelAi = ""
    if model == "1":
        modelAi = "ollama"
    elif model == "2":
        tongyiApi = input("请输入通义千问api token：")
        modelAi = "tongyi"
    # 修改: 支持OpenAI兼容服务并添加模型名称输入
    elif model == "3":
        openaiApiKey = input("请输入OpenAI API Key：")
        openaiEndpoint = input("请输入OpenAI API Endpoint（默认为https://api.siliconflow.com/v1/chat/completions）：") or "https://api.siliconflow.com/v1/chat/completions"
        model_name = input("请输入模型名称（默认为Qwen/Qwen3-VL-32B-Instruct）：") or "Qwen/Qwen3-VL-32B-Instruct"
        modelAi = "openai"
    else:
        print("输入有误")
        sys.exit(0)
else:
    parser = argparse.ArgumentParser()

    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--url')
    parser.add_argument('--api-type', choices=['tongyi', 'openai', 'ollama'], default='tongyi')  # 修改: 添加ollama选项
    parser.add_argument('--tongyi-api')
    parser.add_argument('--openai-api-key')
    parser.add_argument('--openai-endpoint', default='https://api.openai.com/v1/chat/completions')
    parser.add_argument('--model-name', default='gpt-3.5-turbo')  # 新增: 模型名称参数

    args = parser.parse_args()

    username = args.username
    password = args.password
    url = args.url
    modelAi = args.api_type
    
    if modelAi == 'tongyi':
        tongyiApi = args.tongyi_api
    elif modelAi == 'openai':
        openaiApiKey = args.openai_api_key
        openaiEndpoint = args.openai_endpoint
        model_name = args.model_name  # 新增: 获取模型名称参数


# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建chromedriver目录路径
chromedriver_dir = os.path.join(script_dir, 'chromedriver')

options = webdriver.ChromeOptions()
options.binary_location = os.path.join(chromedriver_dir, 'chrome.exe')
options.add_argument('--no-sandbox')
options.add_experimental_option('detach', True)
browser = webdriver.Chrome(service=ChromeService(executable_path=os.path.join(chromedriver_dir, 'chromedriver.exe')), options=options)
browser.maximize_window()

# 在 browser.get(url) 前添加 URL 验证
def validate_url(url):
    # 检查是否为有效 URL
    if not url or not isinstance(url, str):
        raise ValueError("URL 不能为空且必须为字符串")
    
    # 使用正则表达式验证 URL 格式
    url_pattern = re.compile(
        r'^https?://'  # http:// 或 https://
        r'(www\.)?'    # 可选的 www.
        r'[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*'  # 域名
        r'(:[0-9]{1,5})?'  # 可选的端口
        r'(/.*)?$'      # 可选的路径
    )
    
    if not url_pattern.match(url):
        raise ValueError(f"无效的 URL 格式: {url}")
    
    # 解析 URL 并检查是否有非法字符
    parsed_url = urllib.parse.urlparse(url)
    if not parsed_url.netloc:
        raise ValueError("URL 缺少域名")
    
    return True

# 在 main.py 中调用 validate_url
try:
    validate_url(url)
    browser.get(url)
except ValueError as e:
    print(f"URL 验证失败: {e}")
    sys.exit(1)

phone_input = browser.find_element(By.ID, 'phone')
phone_input.send_keys(username)

password_input = browser.find_element(By.ID, 'pwd')
password_input.send_keys(password)

login_button = browser.find_element(By.ID, 'loginBtn')
login_button.click()

time.sleep(3)

if not os.path.exists('result'):
    os.makedirs('result')

def ollama(text):
    url = "http://10.4.240.253:11434/api/generate"
    data = {
        "model": "qwen2:latest",
        "prompt": f"这是题目：{text} 直接返回给我答案的对应选项 不要描述其他的",
        "stream": False
    }
    response = requests.post(url, json=data)
    res = response.text
    data = json.loads(res)
    ans = data.get("response")
    return ans

def tongyi(text):
    dashscope.api_key = tongyiApi
    text = f"这是题目：{text} 直接返回给我答案的对应字母 不要描述其他的"
    messages = [{'role': 'user', 'content': text}]
    response = dashscope.Generation.call(dashscope.Generation.Models.qwen_max, messages=messages,
                                         result_format='message')
    content = response['output']['choices'][0]['message']['content']

    return content

def ty_tiankong(text,num):
    dashscope.api_key = tongyiApi
    text = f"这是一道填空题,{text},请你进行回答,问题里的$填空内容就是需要回答的地方,一共有{num}个空,请你直接告诉我答案 不要描述其他的 每个答案用换行分隔 返回答案的数量要跟我发的一模一样"
    messages = [{'role': 'user', 'content': text}]
    response = dashscope.Generation.call(dashscope.Generation.Models.qwen_max, messages=messages,
                                         result_format='message')
    content = response['output']['choices'][0]['message']['content']

    return content

def ty_tiankong_img(text,num,img):
    i = 0

    while True:
        text1 = f"这是一道填空题,{text},相关图片信息我已提交,请你进行回答里面的问题,一共有{num}个空,请你直接告诉我答案 不要描述其他的 任何一个空的答案都全部用换行分隔 返回答案的数量要跟我发的一模一样,不要描述其他的"
        print("AI图片处理中，请稍后...")
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": img},
                    {"text": text1}
                ]
            }
        ]
        response = dashscope.MultiModalConversation.call(
            api_key=tongyiApi,
            model='qwen-vl-max-latest',
            messages=messages
        )

        if i > 3:
            print("请求失败次数过多，跳过")
            return "error"

        if response["status_code"] == 200:
            break
        else:
            print("请求失败，正在重试...")
            i += 1
    content = response['output']['choices'][0]['message']['content'][0]['text']
    return content

# 新增: OpenAI格式API调用函数
def openai_chat(text, model_name='gpt-3.5-turbo'):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openaiApiKey}"
    }
    data = {
        "model": model_name,  # 使用传入的模型名称
        "messages": [{"role": "user", "content": text}]
    }
    response = requests.post(openaiEndpoint, headers=headers, json=data)
    
    # 检查响应状态码
    if response.status_code != 200:
        print(f"OpenAI API 请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return "API请求失败"
    
    try:
        response_data = response.json()
        # 检查响应格式
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

def openai_tiankong_img(text, num, img, model_name='gpt-4-vision-preview'):
    i = 0
    while True:
        text1 = f"这是一道填空题,{text},相关图片信息我已提交,请你进行回答里面的问题,一共有{num}个空,请你直接告诉我答案 不要描述其他的 任何一个空的答案都全部用换行分隔 返回答案的数量要跟我发的一模一样,不要描述其他的"
        print("AI图片处理中，请稍后...")
        
        # OpenAI不直接支持图片URL，需要转换为base64或使用其他方式
        # 这里简化处理，将图片URL添加到prompt中
        text_with_img = f"{text1}\n图片URL: {img}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openaiApiKey}"
        }
        data = {
            "model": model_name,  # 使用传入的模型名称
            "messages": [{"role": "user", "content": text_with_img}]
        }
        
        response = requests.post(openaiEndpoint, headers=headers, json=data)
        
        if i > 3:
            print("请求失败次数过多，跳过")
            return "error"

        if response.status_code == 200:
            try:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content']
                else:
                    print("API 响应格式错误，缺少 'choices' 字段")
                    print(f"响应内容: {response_data}")
            except Exception as e:
                print(f"解析JSON响应时出错: {e}")
                print(f"响应内容: {response.text}")
        else:
            print(f"请求失败，错误码: {response.status_code}，正在重试...")
        
        i += 1
    
    return "API请求失败"

# 新增: 统一的AI响应获取函数
def get_ai_response(prompt, num=None, img=None, model_name=None):
    if modelAi == "ollama":
        return ollama(prompt)
    elif modelAi == "tongyi":
        if img:
            return ty_tiankong_img(prompt, num, img)
        elif num:
            return ty_tiankong(prompt, num)
        else:
            return tongyi(prompt)
    elif modelAi == "openai":
        if img:
            return openai_tiankong_img(prompt, num, img, model_name)
        elif num:
            return openai_tiankong(prompt, num, model_name)
        else:
            return openai_chat(prompt, model_name)
    else:
        raise ValueError("Unsupported AI model type")

def extract_question_and_options():
        # que_ele = browser.find_element(By.XPATH,"//div[@style='overflow:hidden;']")
        num_ele = browser.find_element(By.XPATH,"//h3[@class='mark_name colorDeep']")

        if "单选" in num_ele.text:
            # type_ele = browser.find_element(By.XPATH,"//span[@class='colorShallow']")
            # type_text = type_ele.text.split("(")[1].split(",")[0]

            options = browser.find_elements(By.XPATH, "//div[@class='clearfix answerBg singleoption']")
            choose = ""
            for option in options:
                option_letter = option.find_element(By.XPATH, ".//span").text
                option_content = option.find_element(By.XPATH, ".//div").text
                choose += f"{option_letter}: {option_content} "

            que = f"{num_ele.text} {choose}"
            print(que)

            # 修改: 传递model_name参数
            ans = get_ai_response(que, model_name=model_name)
            print("AI参考答案：" + ans)
            if 'A' in ans:
                A = browser.find_element(By.XPATH, "//span[text()='A']")
                A.click()

            if 'B' in ans:
                B = browser.find_element(By.XPATH, "//span[text()='B']")
                B.click()

            if 'C' in ans:
                C = browser.find_element(By.XPATH, "//span[text()='C']")
                C.click()

            if 'D' in ans:
                D = browser.find_element(By.XPATH, "//span[text()='D']")
                D.click()

            if 'A' not in ans and 'B' not in ans and 'C' not in ans and 'D' not in ans:
                print("答案获取失败")
                extract_question_and_options()

            time.sleep(1)
            status = click_next_button()
            if status == False:
                sys.exit(0)
        elif "多选" in num_ele.text:
            options = browser.find_elements(By.XPATH, "//div[@class='clearfix answerBg']")
            choose = ""
            for option in options:
                option_letter = option.find_element(By.XPATH, ".//span").text
                option_content = option.find_element(By.XPATH, ".//div").text
                choose += f"{option_letter}: {option_content} "

            que = f"{num_ele.text} {choose}"
            print(que)

            # 修改: 传递model_name参数
            ans = get_ai_response(que, model_name=model_name)

            print("AI参考答案：" + ans)
            if 'A' in ans:
                A = browser.find_element(By.XPATH, "//span[text()='A']")
                A.click()

            if 'B' in ans:
                B = browser.find_element(By.XPATH, "//span[text()='B']")
                B.click()

            if 'C' in ans:
                C = browser.find_element(By.XPATH, "//span[text()='C']")
                C.click()

            if 'D' in ans:
                D = browser.find_element(By.XPATH, "//span[text()='D']")
                D.click()

            if 'A' not in ans and 'B' not in ans and 'C' not in ans and 'D' not in ans:
                print("答案获取失败")
                extract_question_and_options()

            time.sleep(1)
            status = click_next_button()
            if status == False:
                sys.exit(0)
        elif "判断" in num_ele.text:
            que = f"{num_ele.text}"
            print(que)

            # 修改: 传递model_name参数
            ans = get_ai_response(que + "判断题返回对或错", model_name=model_name)

            print("AI参考答案：" + ans)

            if '对' in ans or 'A' in ans or 'T' in ans:
                A = browser.find_element(By.XPATH, "//span[text()='A']")
                A.click()

            if '错' in ans or 'B' in ans or 'F' in ans:
                B = browser.find_element(By.XPATH, "//span[text()='B']")
                B.click()

            if '对' not in ans and '错' not in ans and 'A' not in ans and 'B' not in ans and 'F' not in ans and 'T' not in ans:
                print("答案获取失败")
                extract_question_and_options()

            time.sleep(1)
            status = click_next_button()
            if status == False:
                sys.exit(0)
        elif "填空" in num_ele.text:
            kong = browser.find_elements(By.XPATH,"//div[@class='stem_answer']/div[@class='Answer']")
            kong_num = len(kong)
            que = f"{num_ele.text}"

            image = False
            print(que)

            try:
                img = num_ele.find_element(By.XPATH, ".//img")
                print("获取到题目图片，正在处理...")
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                img_url = img.get_attribute("src")
                # print(f"图片的 URL 是: {img_src}")
                if img_url:  # 确保 URL 不为空
                    # 下载图片
                    response = requests.get(img_url, stream=True, headers=headers)
                    if response.status_code == 200:
                        img_name = img_url.split("/")[-1]
                        img_path = os.path.join(".", img_name)
                        with open(img_path, "wb") as file:
                            for chunk in response.iter_content(1024):
                                file.write(chunk)
                        print(f"图片已获取成功，正在转直链...")
                        # image = True
                    else:
                        print(f"无法加载图片: {img_url}")
                else:
                    print("未找到图片 URL")
                url = "https://image.myxuebi.top/api/v1/upload"
                file = open(img_name, "rb")
                files = {
                    "file": file  # 以二进制模式打开文件
                }

                response = requests.post(url, files=files)
                if response.status_code == 200:
                    res = json.loads(response.text)
                    url_img = res["data"]["links"]["url"]
                    # print(url)
                    # print("图片加载成功！")
                    image = True
                else:
                    print("提交失败，网络错误！")
            except NoSuchElementException:
                pass
            # img_url = img.get_attribute("src")

            if (modelAi == "ollama"):
                print("暂不支持ollama填空")
                status = click_next_button()
                if status == False:
                    sys.exit(0)
            else:
                if image == True:
                    print("图片已成功生成直链：" + url_img)
                    file.close()
                    os.remove(img_name)
                    # 修改: 传递model_name参数
                    ans = get_ai_response(que, kong_num, url_img, model_name)
                    if ans == "error":
                        status = click_next_button()
                        if status == False:
                            sys.exit(0)
                else:
                    # 修改: 传递model_name参数
                    ans = get_ai_response(que, kong_num, model_name)
            ans_list = ans.split("\n")
            ans_list = list(filter(None,ans_list))
            print("AI参考答案：" + str(ans_list))

            if len(ans_list) == kong_num:
                j = 0
                for i in kong:
                    input_bar = i.find_element(By.XPATH, ".//iframe")
                    # WebDriverWait(browser, 10).until(EC.frame_to_be_available_and_switch_to_it(input_bar))
                    # input_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "input")))
                    input_bar.click()
                    input_bar.send_keys(ans_list[j])
                    input_bar.click()
                    j = j + 1
                    # browser.switch_to.default_content()
            else:
                print("错误：AI答案与实际空不符，跳过此题")
                status = click_next_button()
                if status == False:
                    sys.exit(0)

            # sys.exit(0)

            time.sleep(2)
            status = click_next_button()
            if status == False:
                sys.exit(0)

        else:
            print("暂不支持填空")
            status = click_next_button()
            if status == False:
                sys.exit(0)

def click_next_button():
    try:
        next_button = browser.find_element(By.XPATH, '//a[text()="下一题"]')
        next_button.click()
    except NoSuchElementException:
        print("没有找到“下一题”按钮，可能是已经到达最后一题。")
        print("题目填写已结束，请自行检查是否有遗漏，本程序不支持部分解答题等题目，请手动填写")
        print("填空题可能会有错误，请手动核查！")
        print("程序已退出，driver已关闭，请答题完成后手动关闭浏览器")
        os.system('taskkill /im chromedriver.exe /F')
        return False
    except Exception as e:
        print(f"点击下一题按钮失败: {e}")
        return False
    return True

def getque():
    while True:
        time.sleep(0.5)
        extract_question_and_options()

getque()

# browser.quit()
