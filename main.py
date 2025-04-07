import os
import sys

# 路径定义
input_file_path = "./results/result.txt"
output_file_path = "./results/result_path.txt"
device_path = "/dev/sda1"

# 获取容器 UpperDir 和 LowerDir 信息
def get_overlay_paths(container_name):
    info = os.popen(f"docker container inspect {container_name}").readlines()
    lower_dirs = []
    upper_dir = ""
    for line in info:
        if "LowerDir" in line:
            raw = line.split('\"')[-2]
            if ':' in raw:
                lower_dirs = [d[11:] for d in raw.split(':') if "init" not in d]
        elif "UpperDir" in line:
            upper_dir = line.split('\"')[-2][11:]
    return upper_dir, lower_dirs

# 收集每个容器的 overlay 路径（编号与列表位置绑定）
upper_dirs = []
lower_dirs = []
for i in range(1, 7):
    u, l = get_overlay_paths(f"docker_blktest{i}")
    upper_dirs.append(u)
    lower_dirs.append(l)  # 形成二维列表，index 对应容器编号 - 1

# 读取 trace 日志
with open(input_file_path, "r") as infile:
    trace_lines = infile.readlines()

result_lines = []

# 处理每一行 trace
for i, line in enumerate(trace_lines):
    try:
        block_str = line.strip().split()[-1]
        block = int(eval(block_str) / 8)

        # 使用 debugfs 获取 inode
        icheck_cmd = f"debugfs -R 'icheck {block}' {device_path}"
        icheck_result = os.popen(icheck_cmd).readlines()
        if not icheck_result:
            continue
        inode_line = icheck_result[-1]
        inode_parts = inode_line.strip().split()
        if not inode_parts or not inode_parts[-1].isdigit():
            continue
        inode = int(inode_parts[-1])
        if inode == 8:
            continue  # 跳过系统 inode

        # 获取路径
        ncheck_cmd = f"debugfs -R 'ncheck {inode}' {device_path}"
        ncheck_result = os.popen(ncheck_cmd).readlines()
        if not ncheck_result:
            continue
        path_line = ncheck_result[-1].strip()
        file_path = path_line.split()[-1]

        # 判断归属容器及层级
        label = ""
        container_id = -1
        for idx in range(6):
            if file_path.startswith(upper_dirs[idx]):
                label = "[UpperLayer]"
                container_id = idx + 1
                break
            elif any(ld in file_path for ld in lower_dirs[idx]):
                label = "[LowerLayer]"
                container_id = idx + 1
                break

        if label and container_id != -1:
            result_lines.append(f"{line.strip()}\t{file_path}\t{label}\t[Container{container_id}]\n")

    except Exception as e:
        print(f"\nError at line {i}: {e}")
        continue

    # 显示进度
    sys.stdout.write(f"\rProcessing: {i+1}/{len(trace_lines)} ({(i+1)/len(trace_lines)*100:.2f}%)")
    sys.stdout.flush()

# 写入结果
with open(output_file_path, "w") as outfile:
    outfile.writelines(result_lines)

print("\nProcessing complete! Result written to result_path.txt.")

