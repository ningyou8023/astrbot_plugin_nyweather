# AstrBot 天气查询插件

这是一个为 AstrBot 开发的天气查询插件，支持查询当天与多天预报，并根据配置返回 `text` 或由接口直接返回的 `image`。

## 功能特色

- 🌤 查询指定城市当天或多天的天气预报
- 🔄 根据需要自动拼接 `action=forecast` 和 `days`
- 🖼 支持图片、文本两种返回格式
- ⚡ 异步请求，响应更快

## 安装方法

1. 将插件文件夹 `astrbot_plugin_nyweather` 放入 AstrBot 的插件目录
2. 安装依赖：
   ```bash
   pip install aiohttp
   ```
3. 重启 AstrBot

## 使用方法

### 基本命令

- `/天气 城市 [天数]` — 查询指定城市天气；不填或填 1 表示当天
- `/nyweather 城市 [天数]` — 英文命令
- `/天气帮助` — 显示帮助信息

### 示例

```
/天气 北京            # 当天（不拼接 action）
/天气 北京 5          # 5 天预报（拼接 action=forecast&days=5）
```

## 配置说明

插件支持以下配置项（见 `_conf_schema.json`）：

- `api_url`：API 接口地址（默认：`https://api.nycnm.cn/API/weather.php`）
- `api_key`：API 密钥（如果需要）
- `default_format`：返回格式（`text`/`image`，默认：`text`）

## API 接口与参数

- 基础地址：`https://api.nycnm.cn/API/weather.php`
- 必填参数：
  - `query`：城市，如：`北京`
  - `format`：返回格式，`text`/`image`
- 选填参数：
  - `action`：当查询多天天气时需填写 `forecast`
  - `days`：查询天数，最多 8 天；仅在多天时有效
  - `apikey`：密钥（如服务端要求，需到柠柚API https://api.nycnm.cn 注册获取）

### URL 拼接规则（关键说明）

- 查询当天：不添加 `action` 和 `days`
  - 示例：`https://api.nycnm.cn/API/weather.php?query=北京&format=text`
- 查询多天：必须添加 `action=forecast`，并附加 `days`
  - 示例：`https://api.nycnm.cn/API/weather.php?query=北京&format=image&action=forecast&days=5`

## 返回说明

- 当 `default_format=image` 时，插件直接返回接口生成的图片；若图片获取失败，自动降级为文本。
- 文本模式下，插件直接输出接口返回的文本内容。

## 注意事项

1. 天数不填写或为 1 时，视为当天查询，不拼接 `action`。
2. 天数 ≥ 2 时，拼接 `action=forecast` 与 `days=n`（最多 8）。
3. 请确保网络可访问接口地址，必要时配置 `apikey`。

## 版本历史

- v1.0.0：初始版本，支持当天与多天查询、图片返回

## 许可证

MIT License