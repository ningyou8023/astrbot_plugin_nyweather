import asyncio
import aiohttp
import tempfile
from urllib.parse import quote
import os
from pathlib import Path

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

PLUGIN_DATA_DIR = Path("data", "plugins_data", "astrbot_nyweather")
PLUGIN_DATA_DIR.mkdir(parents=True, exist_ok=True)

@register(
    "astrbot_nyweather",
    "柠柚",
    "天气查询插件，支持当天与多天预报，返回text/image",
    "1.0.0",
)
class WeatherPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.api_url = getattr(config, "api_url", "https://api.nycnm.cn/API/weather.php")
        self.api_key = getattr(config, "api_key", "")
        self.default_format = getattr(config, "default_format", "image")
        logger.info("天气查询插件初始化完成")

    @filter.command("nyweather", alias={"天气", "天气查询", "查天气"})
    async def query_weather(self, event: AstrMessageEvent):
        message_text = event.get_message_str()
        parts = message_text.strip().split()
        if len(parts) < 2:
            await event.send("❌ 参数不足\n\n用法: /天气 城市 [天数]\n示例: /天气 北京 或 /天气 北京 5")
            return

        city = parts[1]
        days = None
        if len(parts) >= 3:
            try:
                d = int(parts[2])
                if d >= 2:
                    days = d
            except Exception:
                days = None

        try:
            if str(self.default_format).lower() == "image":
                image_path = await self._query_weather_image(city, days)
                if image_path:
                    yield event.image_result(image_path)
                    try:
                        os.unlink(image_path)
                    except Exception:
                        pass
                else:
                    text = await self._query_weather_text(city, days)
                    if text:
                        title = f"📍 {city}天气" if not days else f"📍 {city}{days}天天气预报"
                        yield event.plain_result(f"{title}\n\n{text}")
                    else:
                        yield event.plain_result("❌ 查询失败或无数据")
            else:
                text = await self._query_weather_text(city, days)
                if text:
                    title = f"📍 {city}天气" if not days else f"📍 {city}{days}天天气预报"
                    yield event.plain_result(f"{title}\n\n{text}")
                else:
                    yield event.plain_result("❌ 查询失败或无数据")
        except Exception as e:
            logger.error(f"查询天气时发生错误: {e}")
            yield event.plain_result(f"❌ 查询失败: {str(e)}")

    @filter.command("help_nyweather", alias={"天气帮助"})
    async def show_help(self, event: AstrMessageEvent):
        help_text = (
            "🧭 天气查询插件\n\n"
            "用法:\n"
            "• /天气 城市 [天数]\n"
            "示例:\n"
            "• /天气 北京\n"
            "• /天气 北京 5\n\n"
            "说明:\n"
            "• 不填写天数或填写1则查询当天，不拼接action\n"
            "• 填写≥2天则拼接action=forecast并附加days\n"
        )
        yield event.plain_result(help_text)

    async def _query_weather_text(self, city: str, days: int | None) -> str | None:
        try:
            url = self._build_url(city, days, fmt="text")
            logger.info(f"请求URL: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        text_data = await response.text()
                        return text_data if text_data else None
                    return None
        except asyncio.TimeoutError:
            logger.error("API请求超时")
            return None
        except Exception as e:
            logger.error(f"获取文本数据时发生错误: {e}")
            return None

    async def _query_weather_image(self, city: str, days: int | None) -> str | None:
        try:
            url = self._build_url(city, days, fmt="image")
            logger.info(f"请求URL(图片): {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        data = await response.read()
                        if not data:
                            return None
                        suffix = ".png" if "png" in content_type.lower() else ".jpg" if ("jpeg" in content_type.lower() or "jpg" in content_type.lower()) else ".img"
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                        temp_file.write(data)
                        temp_file.close()
                        return temp_file.name
                    return None
        except asyncio.TimeoutError:
            logger.error("API请求超时(图片)")
            return None
        except Exception as e:
            logger.error(f"获取图片时发生错误: {e}")
            return None

    def _build_url(self, city: str, days: int | None, fmt: str) -> str:
        q = quote(city)
        url = f"{self.api_url}?query={q}&format={fmt}"
        if days and days >= 2:
            url += f"&action=forecast&days={days}"
        if self.api_key:
            url += f"&apikey={self.api_key}"
        return url

    async def terminate(self):
        logger.info("天气查询插件已终止")