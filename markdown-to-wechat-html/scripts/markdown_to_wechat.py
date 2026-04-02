#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("请先安装 markdown 库: pip install markdown")
    sys.exit(1)


WECHAT_CSS = """
<style>
    :root {
        --primary-color: #333;
        --secondary-color: #888;
        --bubble-bg: #f8f8f8;
        --quote-bg: #fdfdfd;
        --accent-color: #ff9800;
        --qa-q-color: #333;
        --qa-a-color: #333;
    }
    .markdown-here-wrapper {
        font-size: 16px;
        line-height: 1.8;
        letter-spacing: 0.05em;
        padding: 0 16px;
        background-color: #fff;
        max-width: 677px;
        margin: 0 auto;
        color: #333;
    }
    body {
        margin: 0;
        padding: 0;
        font-family: -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
        background-color: #fff;
    }
    p {
        margin: 1.5em 0;
        line-height: 1.8;
        text-align: justify;
    }
    h1, h2, h3, h4, h5, h6 {
        margin: 2em 0 1em;
        line-height: 1.4;
        font-weight: bold;
        color: var(--primary-color);
        text-align: center;
    }
    h1 { font-size: 24px; margin-bottom: 24px; }
    h2 { 
        font-size: 20px; 
        margin-top: 2.5em;
        margin-bottom: 0.2em;
    }
    /* Section Divider Style */
    .section-divider {
        text-align: center;
        color: #ddd;
        font-size: 12px;
        letter-spacing: 4px;
        margin-bottom: 2em;
    }
    img {
        max-width: 100% !important;
        height: auto !important;
        display: block;
        margin: 20px auto;
        border-radius: 4px;
    }
    blockquote {
        background: #fdfdfd;
        border-left: 3px solid #ccc;
        padding: 15px 20px;
        margin: 20px 0;
        color: #555;
        font-style: normal;
    }
    blockquote p {
        margin: 0;
        line-height: 1.8;
    }
    code {
        font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
        font-size: 14px;
        background-color: #f7f7f7;
        padding: 2px 4px;
        border-radius: 3px;
    }
    pre {
        background-color: #f7f7f7;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        margin: 20px 0;
    }
    pre code {
        background-color: transparent;
        padding: 0;
        border-radius: 0;
    }
    hr {
        border: 0;
        border-top: 1px solid #eee;
        margin: 30px auto;
        width: 80%;
    }
    ul, ol {
        margin: 1.5em 0;
        padding-left: 2em;
    }
    li {
        margin: 0.5em 0;
    }
    strong {
        color: #333;
        font-weight: bold;
    }
    em {
        color: #888;
        font-style: italic;
    }
    a {
        color: #576b95;
        text-decoration: none;
    }
    /* Chat Bubble Styles */
    .bubble-container {
        margin: 20px 0;
    }
    .bubble-header {
        font-weight: bold;
        margin-bottom: 8px;
        text-align: left;
    }
    .bubble-content {
        background-color: #FFF9E6; /* Light cream/yellow */
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #FDF0C2;
        position: relative;
    }
    .bubble-content p:last-child {
        margin-bottom: 0;
    }
    .bubble-content p:first-child {
        margin-top: 0;
    }
    /* Q&A Styles */
    .qa-block {
        margin: 24px 0;
    }
    .qa-q {
        display: flex;
        align-items: flex-start;
        margin-bottom: 12px;
    }
    .qa-q-icon {
        background: #333;
        color: #fff;
        width: 24px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        border-radius: 4px;
        font-size: 14px;
        font-weight: bold;
        flex-shrink: 0;
        margin-top: 4px;
        margin-right: 12px;
    }
    .qa-q-text {
        font-weight: bold;
        line-height: 1.8;
    }
    .qa-a {
        display: flex;
        align-items: flex-start;
        background: #f8f8f8;
        padding: 16px;
        border-radius: 8px;
    }
    .qa-a-icon {
        background: #888;
        color: #fff;
        width: 24px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        border-radius: 4px;
        font-size: 14px;
        font-weight: bold;
        flex-shrink: 0;
        margin-right: 12px;
        margin-top: 4px;
    }
    .qa-a-text {
        line-height: 1.8;
    }
    /* Metadata Styles */
    .wechat-title-box {
        text-align: center;
        padding: 40px 20px 20px;
    }
    .wechat-title {
        font-size: 24px;
        line-height: 1.4;
        font-weight: bold;
        margin-bottom: 16px;
    }
    .wechat-author-line {
        color: #888;
        font-size: 14px;
        margin-bottom: 10px;
    }
</style>
"""


class WeChatMarkdownConverter:
    def __init__(self, image_dir=None):
        self.image_dir = image_dir
        self.title = ""
        self.author = ""
        self.wechat_name = ""

    def extract_metadata(self, md_content):
        lines = md_content.strip().split('\n')
        metadata = {}

        first_line = True
        for line in lines:
            line_stripped = line.strip()

            if first_line and line_stripped.startswith('# '):
                self.title = line_stripped[2:].strip()
                first_line = False
                continue

            first_line = False

            if ':' in line_stripped:
                key, value = line_stripped.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key in ['author', '作者']:
                    self.author = value
                elif key in ['公众号', 'wechat_name']:
                    self.wechat_name = value
                elif key == 'title' and not self.title:
                    self.title = value

        return md_content

    def convert(self, md_content):
        self.extract_metadata(md_content)

        # 1. Custom Components (Handle these before generic markdown formatting)
        
        # Section Headers & Dividers (e.g. **01 嘉宾介绍** \n\n ■ ■ ■ ■)
        def handle_section_header(match):
            title = match.group(1).strip()
            return f'<h2>{title}</h2><div class="section-divider">■ ■ ■ ■</div>'
        md_content = re.sub(r'^\*\*(\d+\s+.+)\*\*\n\n■ ■ ■ ■', handle_section_header, md_content, flags=re.MULTILINE)

        # Q&A blocks
        # Pattern: **Q** \n\n **question** \n\n **A** \n\n answer (multi-line)
        def handle_qa(match):
            q_text = match.group(1).strip()
            a_text = match.group(2).strip()
            return f'<div class="qa-block"><div class="qa-q"><div class="qa-q-icon">Q</div><div class="qa-q-text">{q_text}</div></div><div class="qa-a"><div class="qa-a-icon">A</div><div class="qa-a-text">{a_text}</div></div></div>'
        
        # Match until next **Q** or next section header
        md_content = re.sub(r'^\*\*Q\*\*\n\n\*\*(.+?)\*\*\n\n\*\*A\*\*\n\n((?:(?!\*\*Q\*\*|^\*\*?\d).+\n?)+)', handle_qa, md_content, flags=re.MULTILINE)

        # Chat Bubbles (Names)
        # Pattern: **Name** \n\n content (multi-line)
        def handle_bubble(match):
            name = match.group(1).strip()
            content = match.group(2).strip()
            if name in ['Q', 'A', '作者', '公众号', 'Author', 'Title', '文章目录', '目录']:
                return match.group(0)
            return f'<div class="bubble-container"><div class="bubble-header">{name}</div><div class="bubble-content">{content}</div></div>'

        # This regex matches a bold name at start of line, followed by some content that doesn't start with bold name or section
        md_content = re.sub(r'^\*\*([^*]+)\*\*\n\n((?:(?!^\*\*).+\n?)+)', handle_bubble, md_content, flags=re.MULTILINE)

        # Special case for "文章目录"
        md_content = re.sub(r'^\*\*文章目录\*\*\s*$', r'<div style="text-align: center; font-weight: bold; margin: 2em 0;">文章目录</div>', md_content, flags=re.MULTILINE)

        # Intro Quote Box
        def handle_intro_quote(match):
            quote = match.group(1).strip()
            author = match.group(2).strip()
            return f'<div style="background: #f9f9f9; border: 1px solid #eee; border-radius: 8px; padding: 20px; margin: 20px 0; font-family: KaiTi, STKaiti, serif;"><p style="margin: 0; line-height: 1.8;">“{quote}”</p><p style="margin: 10px 0 0; text-align: right; color: #888;">——{author}</p></div>'
        
        md_content = re.sub(r'^“(.+?)”\n\s*\n——(.+?)$', handle_intro_quote, md_content, flags=re.MULTILINE)

        # Swipe indicator
        md_content = re.sub(r'^（\n\s*左右滑动查看更多\n\s*）$', r'<div style="text-align: center; color: #aaa; font-size: 14px; margin: 10px 0;">（ 左右滑动查看更多 ）</div>', md_content, flags=re.MULTILINE)

        # 2. Standard Markdown Formatting:
        
        md_content = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', md_content, flags=re.MULTILINE)
        md_content = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', md_content, flags=re.MULTILINE)
        md_content = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', md_content, re.MULTILINE)

        md_content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', md_content)
        md_content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', md_content)

        md_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', self._process_image, md_content)

        md_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', md_content)

        code_block_pattern = r'```(\w*)\n(.*?)```'
        md_content = re.sub(code_block_pattern, r'<pre><code>\2</code></pre>', md_content, flags=re.DOTALL)

        md_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', md_content)

        blockquote_pattern = r'^>\s*(.+)$'
        md_content = re.sub(blockquote_pattern, r'<blockquote>\1</blockquote>', md_content, flags=re.MULTILINE)

        table_pattern = r'^\|(.+)\|\n\|[-|]+\|\n((?:\|.+\|\n?)+)'
        def process_table(match):
            headers = match.group(1).split('|')
            headers = [h.strip() for h in headers if h.strip()]
            rows = match.group(2).strip().split('\n')
            html = '<table>'
            html += '<thead><tr>'
            for h in headers:
                html += f'<th>{h}</th>'
            html += '</tr></thead><tbody>'
            for row in rows:
                cells = row.split('|')
                cells = [c.strip() for c in cells if c.strip()]
                html += '<tr>'
                for c in cells:
                    html += f'<td>{c}</td>'
                html += '</tr>'
            html += '</tbody></table>'
            return html
        md_content = re.sub(table_pattern, process_table, md_content, flags=re.MULTILINE)

        hr_pattern = r'^---+$'
        md_content = re.sub(hr_pattern, '<hr>', md_content, flags=re.MULTILINE)

        lines = md_content.split('\n')
        result_lines = []
        in_list = False
        in_paragraph = False

        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                if in_paragraph:
                    result_lines.append('</p>')
                    in_paragraph = False
                continue

            if re.match(r'^[-*]\s+', line):
                if in_paragraph:
                    result_lines.append('</p>')
                    in_paragraph = False
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                content = re.sub(r'^[-*]\s+', '', line)
                result_lines.append(f'<li>{content}</li>')
            elif re.match(r'^\d+\.\s+', line):
                if in_paragraph:
                    result_lines.append('</p>')
                    in_paragraph = False
                if not in_list:
                    result_lines.append('<ol>')
                    in_list = True
                content = re.sub(r'^\d+\.\s+', '', line)
                result_lines.append(f'<li>{content}</li>')
            elif line.startswith('<'):
                if in_paragraph:
                    result_lines.append('</p>')
                    in_paragraph = False
                result_lines.append(line)
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                if not in_paragraph:
                    result_lines.append(f'<p>{line}')
                    in_paragraph = True
                else:
                    result_lines.append(f' {line}')

        if in_list:
            result_lines.append('</ul>')
        if in_paragraph:
            result_lines.append('</p>')

        return '\n'.join(result_lines)

    def _process_image(self, match):
        alt_text = match.group(1)
        image_path = match.group(2)

        if self.image_dir and not image_path.startswith('http'):
            image_name = os.path.basename(image_path)
            image_path = os.path.join(self.image_dir, image_name)

        return f'<img src="{image_path}" alt="{alt_text}">'

    def generate_html(self, md_content):
        # Extract title and author first so we can remove them from the main content if needed
        self.extract_metadata(md_content)
        
        # Remove the title and author lines from md_content to avoid duplication
        # This is very basic, but for this specific file it should work
        # Title is usually # Title
        md_content = re.sub(r'^#\s+.+\n+', '', md_content)
        # Author line (作者: ...)
        md_content = re.sub(r'^(作者|作者:)\s+.+\n+', '', md_content, flags=re.MULTILINE)
        # Wechat name line (公众号: ...)
        md_content = re.sub(r'^(公众号|公众号:)\s+.+\n+', '', md_content, flags=re.MULTILINE)

        html_content = self.convert(md_content)

        title_section = ""
        if self.title:
            author_line = ""
            if self.author:
                author_line = f'<div class="wechat-author-line">{self.author}</div>'
            title_section = f"""
<div class="wechat-title-box">
    <h1 class="wechat-title">{self.title}</h1>
    {author_line}
</div>"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    {WECHAT_CSS}
</head>
<body>
<div class="markdown-here-wrapper">
{title_section}
{html_content}
</div>
</body>
</html>"""
        return html


def main():
    parser = argparse.ArgumentParser(description='将 Markdown 转换为微信公众号 HTML')
    parser.add_argument('markdown_file', help='输入的 Markdown 文件')
    parser.add_argument('--output', '-o', help='输出的 HTML 文件路径')
    parser.add_argument('--author', '-a', help='文章作者')
    parser.add_argument('--copyright', '-c', type=int, default=0, choices=[0, 1, 2], help='原创声明: 0-原创, 1-转载, 2-授权转载')
    parser.add_argument('--image-dir', help='图片目录路径')

    args = parser.parse_args()

    if not os.path.exists(args.markdown_file):
        print(f"错误: 文件不存在: {args.markdown_file}")
        sys.exit(1)

    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    converter = WeChatMarkdownConverter(image_dir=args.image_dir)

    if args.author:
        converter.author = args.author

    html_content = converter.generate_html(md_content)

    if args.output:
        output_path = args.output
    else:
        md_path = Path(args.markdown_file)
        output_path = str(md_path.with_suffix('.html'))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ 转换完成!")
    print(f"标题: {converter.title}")
    print(f"作者: {converter.author}")
    print(f"输出文件: {output_path}")
    print(f"\n可直接复制 body 内的内容到微信编辑器使用")


if __name__ == '__main__':
    main()
