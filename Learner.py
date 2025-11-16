# -*- coding: utf-8 -*-
import logging
import requests
import datetime
import os
import xml.etree.ElementTree as ET
from email.utils import format_datetime

"""
配置logging模块
"""
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('Learner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Requester:
    def __init__(self):
        pass

    def Getter(self):
        pass
class Sender:
    def __init__(self):
        pass

    def Send(self) -> str:
        pass

class OpenaiRequester(Requester):
    """
    @brief: Make a Chat by Openai API
    """
    def __init__(self):
        self.__url = "https://api.siliconflow.cn/v1/chat/completions"
        self.__api_key = "sk-dcteuzvdnvgjokfuxgygoeswfabkqvdjrafmxtjazruupuan"
        self.__model = "Qwen/Qwen3-8B"
        self.__headers = {
            "Authorization": f"Bearer {self.__api_key}",
            "Content-Type": "application/json"
        }

        self.systemPrompt = "你是一个全能的高中学习助手，你的任务是推送语文、数学、英语、物理、化学、生物最近信息 \
                            1.将每科资料分别整理好,只要输出markdown格式,其它什么都不要输出, \
                            2.语文：整理作文素材、高考优秀作文全篇 \
                            3.数学：出一题数学压轴小题，要结合高中课本，不要脱离考场、脱离实际，可以不给答案 \
                            4.英语：整理一篇英语时文，非高中英语的词汇要有注释（仅词义）,词数300词左右 \
                            5.物理：每天可以整理一篇文章，来源可以是物理顶刊、诺贝尔物理学奖,阅读时长约5分钟 \
                            6.化学：介绍一些对于高中有用的知识 \
                            6.生物：做一个类似记忆卡片的内容，用来复习高中生物"

    def Getter(self, content: str):
        logger.info(f"{__class__}请求对话 内容: {content}")
        try:
            self.payload = {
                "model": self.__model,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{content}"
                    },
                    {
                        "role": "system",
                        "content": self.systemPrompt
                    }
                    ]
            }
            response = requests.post(url=self.__url, json=self.payload, headers=self.__headers)
            logger.info(f"收到数据: {response.json()}")
            return response
        except:
            logger.critical(f"发生错误")
        return {}
class RSSSender(Sender):
    def __init__(self, filePath=r"f:\Desktop\Learner\learner.xml",
                 channelTitle="Learner",
                 channelDescription="Learner"):
        self.filePath = filePath
        self.channelTitle = channelTitle
        self.channelDescription = channelDescription

    def _createFeed(self):
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = self.channelTitle
        ET.SubElement(channel, "description").text = self.channelDescription
        return rss, channel

    def Send(self, title: str, content: str, link: str = None, pubdate: datetime.datetime = None) -> str:
        try:
            if os.path.exists(self.filePath):
                tree = ET.parse(self.filePath)
                rss = tree.getroot()
                channel = rss.find("channel")
                if channel is None:
                    rss, channel = self._createFeed()
            else:
                rss, channel = self._createFeed()

            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "description").text = content
            dt = pubdate or datetime.datetime.now(datetime.timezone.utc)
            ET.SubElement(item, "pubDate").text = format_datetime(dt)

            tree = ET.ElementTree(rss)
            tree.write(self.filePath, encoding="utf-8", xml_declaration=True)
            logger.info(f"RSS 已写入: {self.filePath}")
            return self.filePath
        except Exception as e:
            logger.error(f"RssSender 失败: {e}")
            return ""


if __name__ == "__main__":
    openaiRequester = OpenaiRequester()
    res = openaiRequester.Getter("请整理今天的资料")
    print(res.json()["choices"][0]["message"]["content"])

    rss = RSSSender()
    rss.Send(title="Learner", content=res.json()["choices"][0]["message"]["content"])
