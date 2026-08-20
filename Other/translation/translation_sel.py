import requests


def translate(text: str, source_lang: str, target_lang: str) -> str:
    url = "https://api.mymemory.translated.net/get"

    params = {
        "q": text,
        "langpair": f"{source_lang}|{target_lang}"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    if data.get("responseStatus") == 200:
        return data["responseData"]["translatedText"]

    raise Exception(f"翻译失败: {data.get('responseDetails')}")


def main():
    print("===== 简单翻译工具 =====")
    print("1. 中文翻译成英文")
    print("2. 英文翻译成中文")
    print("0. 退出")

    while True:
        choice = input("\n请选择功能：").strip()

        if choice == "0":
            print("退出程序")
            break

        text = input("请输入要翻译的内容：").strip()

        if not text:
            print("输入内容不能为空")
            continue

        try:
            if choice == "1":
                result = translate(text, "zh-CN", "en")
            elif choice == "2":
                result = translate(text, "en", "zh-CN")
            else:
                print("无效选择")
                continue

            print("翻译结果：", result)

        except requests.exceptions.Timeout:
            print("请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            print("网络错误：", e)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
