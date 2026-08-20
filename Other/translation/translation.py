import requests

def translate(text: str, source_lang: str = "zh-CN", target_lang: str = "en") -> str:
    """
    使用 MyMemory 免费翻译接口翻译文本

    :param text: 要翻译的文本
    :param source_lang: 源语言，例如 zh-CN 中文，en 英文
    :param target_lang: 目标语言，例如 en 英文，zh-CN 中文
    :return: 翻译结果
    """
    url = "https://api.mymemory.translated.net/get"

    params = {
        "q": text,
        "langpair": f"{source_lang}|{target_lang}"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if data.get("responseStatus") == 200:
        return data["responseData"]["translatedText"]
    else:
        raise Exception(f"翻译失败: {data.get('responseDetails')}")


if __name__ == "__main__":
    text = input("请输入要翻译的内容：")

    result = translate(text, "zh-CN", "en")
    print("翻译结果：", result)
