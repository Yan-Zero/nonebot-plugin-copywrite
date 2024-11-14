<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://raw.githubusercontent.com/tkgs0/nbpt/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://raw.githubusercontent.com/tkgs0/nbpt/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# Nonebot 2 定型文生成器

_✨ NoneBot 定型文生成器 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Yan-Zero/nonebot-plugin-copywrite.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-copywrite">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-copywrite.svg" alt="pypi">
</a>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="python">
</a>
<a href="https://nonebot.dev">
    <img src="https://img.shields.io/badge/nonebot-2.4.0+-red.svg" alt="nonebot">
</a>
<a href="https://onebot.adapters.nonebot.dev">
    <img src="https://img.shields.io/badge/OneBot-11-black?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHAAAABwCAMAAADxPgR5AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAAxQTFRF////29vbr6+vAAAAk1hCcwAAAAR0Uk5T////AEAqqfQAAAKcSURBVHja7NrbctswDATQXfD//zlpO7FlmwAWIOnOtNaTM5JwDMa8E+PNFz7g3waJ24fviyDPgfhz8fHP39cBcBL9KoJbQUxjA2iYqHL3FAnvzhL4GtVNUcoSZe6eSHizBcK5LL7dBr2AUZlev1ARRHCljzRALIEog6H3U6bCIyqIZdAT0eBuJYaGiJaHSjmkYIZd+qSGWAQnIaz2OArVnX6vrItQvbhZJtVGB5qX9wKqCMkb9W7aexfCO/rwQRBzsDIsYx4AOz0nhAtWu7bqkEQBO0Pr+Ftjt5fFCUEbm0Sbgdu8WSgJ5NgH2iu46R/o1UcBXJsFusWF/QUaz3RwJMEgngfaGGdSxJkE/Yg4lOBryBiMwvAhZrVMUUvwqU7F05b5WLaUIN4M4hRocQQRnEedgsn7TZB3UCpRrIJwQfqvGwsg18EnI2uSVNC8t+0QmMXogvbPg/xk+Mnw/6kW/rraUlvqgmFreAA09xW5t0AFlHrQZ3CsgvZm0FbHNKyBmheBKIF2cCA8A600aHPmFtRB1XvMsJAiza7LpPog0UJwccKdzw8rdf8MyN2ePYF896LC5hTzdZqxb6VNXInaupARLDNBWgI8spq4T0Qb5H4vWfPmHo8OyB1ito+AysNNz0oglj1U955sjUN9d41LnrX2D/u7eRwxyOaOpfyevCWbTgDEoilsOnu7zsKhjRCsnD/QzhdkYLBLXjiK4f3UWmcx2M7PO21CKVTH84638NTplt6JIQH0ZwCNuiWAfvuLhdrcOYPVO9eW3A67l7hZtgaY9GZo9AFc6cryjoeFBIWeU+npnk/nLE0OxCHL1eQsc1IciehjpJv5mqCsjeopaH6r15/MrxNnVhu7tmcslay2gO2Z1QfcfX0JMACG41/u0RrI9QAAAABJRU5ErkJggg==" alt="onebot">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-copywrite" rel="nofollow">
    <img alt="pypi download" src="https://img.shields.io/pypi/dm/nonebot-plugin-copywrite" style="max-width: 100%;">
</a>

</div>

## 📖 介绍

基于 LLM 的定型文生成器

## ⚙️ 数据配置

### 定型文

存放于 ./data/copywrite/ 下面

#### 例子

```yaml
__category__: 114514

鸣潮:
  examples:
    - 圆桌是这样的，亚瑟王只需要使用圣剑就行了，而圆桌骑士们需要考虑的就多了，什么时候和贵妇幽会，什么时候挑起内战，都需要深思熟虑
    - 儿童节是这样的，大哥哥只需要在家等着被抓就行了，而小萝莉要考虑的事情就很多了，什么时候喊杂鱼杂鱼，什么时候掀裙子露内裤，什么时候拉响警报器，都需要经过深思熟虑
    - 企业家是这样的，员工只需要完成工作任务就行了，而老板要考虑的事情就很多了，什么时候拖欠工资，什么时候增加工作时间，员工绩效怎么压，都需要深思熟虑
  addition: "你回复的文案应该是辛辣讽刺的，例如老板考虑如何拖欠工资，学生考虑低分怎么辩解，游戏玩家考虑如何开挂。"
  model: grok-beta
```

#### 解释

- \_\_category\_\_: 定型文的分类
- examples: 例子
- addition: 附加内容，用以约束 LLM 可能的输出
- model: 使用的模型

## 💬 指令

### 文案

> /文案 [Type] (Keywords)* [Topic]

生产电子垃圾。

| 参数 | 说明 |
| ---- | ---- |
| Type | 文案名字 |
| Topic | 文案的主题 |
| Keywords | 文案的关键词 |

> /文案

查看可用文案.

> /文案 [Type]

查看帮助，如果有的话。

#### 保留关键字

只有 SuperAdmin 才能使用。

1. reload: 重新加载定型文数据
2. **fetch**: ！！慎用！！ 调用 pip 更新 nonebot-plugin-copywrite，由于依赖问题，可能下一次bot就无法启动了。

#### 文案 示例

> /文案

```yaml
Yan:
  不是高三生, 乙游大世界, 两种可能, 你说得对, 女性凝视, 二次元, 四不吃, 回来吧, 带节奏, 慢就业, 紧缩术, 恩情, 意林, 饭局, 鸣潮
Life.Checkpoint:
  第一个被抓, 求真学生, 表白
```

---

> /copywrite reload

```yaml
重新加载完成。
```

---

> /文案 鸣潮 造新梗，套公式

```yaml
造新梗是这样的，网友们只需要动动手指发个帖就行了，而梗创作者要考虑的事情就很多了，什么时候抓住热点，怎么巧妙结合时事，如何让梗迅速传播，都需要深思熟虑。
```

#### 文案 Alias

- copywrite

### 汉语新解

Prompt 原作者：[李继刚](https://web.okjike.com/u/752D3103-1107-43A0-BA49-20EC29D09E36)

> /汉语新解 [Word]

将一个汉语词汇进行全新角度的解释。（看模型，GPT-4o 多正能量，Claude 多讽刺，Gemini 比较中庸）

| 参数 | 说明 |
| ---- | ---- |
| Word | 词汇，其实不仅限于汉语。 |

#### 汉语新解 示例

> /汉语新解 调休

![调休](https://linux.do/uploads/default/optimized/3X/8/e/8ef55c54541fe2e152db70151d129054d20e6c6a_2_666x750.png)

#### 汉语新解 Alias

- new-meaning
