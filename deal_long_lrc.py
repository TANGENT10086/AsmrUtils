import re


def convert_lrc_time(lrc_file_path, output_file_path):
    # 打开原始 LRC 文件读取内容
    with open(lrc_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 用于存储转换后的内容
    converted_lines = []

    # 时间戳的正则表达式
    # 适应 [hh:mm:ss.xx] 和 [mm:ss.xx] 格式
    timestamp_pattern = re.compile(r'\[(?:(\d{2}):)?(\d{2}):(\d{2})\.(\d{2})\]')

    for line in lines:
        # 查找时间戳并进行转换
        match = timestamp_pattern.search(line)
        if match:
            # 如果匹配到小时部分
            if match.group(1):  # 有小时部分
                hours = int(match.group(1))  # 小时
                minutes = int(match.group(2))  # 分钟
            else:
                hours = 0  # 没有小时部分
                minutes = int(match.group(2))  # 仅有分钟
            seconds = int(match.group(3))  # 秒
            milliseconds = match.group(4)  # 毫秒

            # 如果小时数大于0，将其转换为分钟
            if hours > 0:
                minutes += hours * 60  # 将小时转为分钟

            # 格式化新的时间戳
            new_timestamp = f"[{minutes:02d}:{seconds:02d}.{milliseconds}]"

            # 替换原来的时间戳
            new_line = line.replace(match.group(0), new_timestamp)
            converted_lines.append(new_line)
        else:
            # 如果没有匹配到时间戳，原样添加该行
            converted_lines.append(line)

    # 将转换后的内容写入到新的文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(converted_lines)

# 使用示例
convert_lrc_time('D:\ASMR\收藏\RJ01115858 N ようこそ悔シコ研究室へ!～憧れの敬語クールな先輩から最近したセックスの話を延々と聞かされる実験～\\04_Case_3「浮浪者」による異常セックス.lrc',
                 'D:\ASMR\\04_Case_3「浮浪者」による異常セックス.lrc')
