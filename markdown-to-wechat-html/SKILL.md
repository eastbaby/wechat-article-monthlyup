---
name: markdown-to-wechat-html
description: 将 Markdown 文件转换为微信公众号文章格式的 HTML。支持提取标题、作者、公众号信息，生成可直接复制到微信编辑器使用的 HTML 代码。
---

# Markdown to WeChat HTML

一个将 Markdown 转换为微信公众号格式 HTML 的 skill。

## 使用场景

- 将本地 Markdown 文件转换为微信公众号可用的 HTML
- 保持微信公众号文章的美观样式
- 支持图片、代码块、引用、表格等元素

## 使用方法

```bash
python scripts/markdown_to_wechat.py <markdown_file> [--output <output_html>] [--author <author_name>] [--copyright <copyright_type>]
```

## 示例

```bash
python scripts/markdown_to_wechat.py "文章.md"
python scripts/markdown_to_wechat.py "文章.md" --output "文章.html"
python scripts/markdown_to_wechat.py "文章.md" --author "作者名" --copyright 1
```

## 参数

- `<markdown_file>`：输入的 Markdown 文件路径
- `--output`：输出的 HTML 文件路径（默认：原文件名 + .html）
- `--author`：文章作者（默认：从 Markdown 元数据提取或留空）
- `--copyright`：原创声明（0：原创，1：转载，2：授权转载，默认：0）
- `--image-dir`：图片目录路径（用于处理本地图片路径）

## 输出结构

生成的文件包含微信公众号风格的 HTML：

- 标题样式（h1, h2, h3）
- 正文样式（段落、引用、代码块）
- 图片样式（居中、最大宽度）
- 表格样式
- 分隔线样式

可直接复制 `<body>` 内的内容到微信编辑器使用。

## 依赖

- Python 3.9+
- markdown

安装依赖：

```bash
pip install markdown
```
