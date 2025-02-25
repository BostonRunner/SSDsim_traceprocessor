##################################################################################
# Python script of handling the output of blkparse and add the path of file      #
# Please change the directory according to your system and device                #
# Author: Ruofei Wu                                                              #
# 09-26-2024                                                                     #
# Renewed in 09-30-2024                                                          #
##################################################################################

import os
import sys
import time

data_with_path = str()
io = str()

# open the log
origin_file = open("./results/result.txt", "r")
final = open("./results/result_path.txt", "w")
info = os.popen("docker container inspect docker_blktest")
info = info.readlines()
LowerDir = str()
LowerDirList = list()
UpperDir = str()

for i in range(len(info)):
    if "LowerDir" in info[i]:
        LowerDir = info[i].split('\"')[-2]
        if ':' in LowerDir:
            LowerDirList = LowerDir.split(':')
        LowerDir = LowerDir[11:]
        print(LowerDirList)
        time.sleep(2)
    elif "UpperDir" in info[i]:
        UpperDir = info[i].split('\"')[-2]
        UpperDir = UpperDir[11:]
        print(UpperDir)
        time.sleep(2)
    else:
        pass

print("File reading")
# read the log
data = origin_file.readlines()

print("File processing")
# read the inode
for i in range(len(data)):
    block = int(eval(data[i].split()[-1]) / 8)

    command = f"debugfs -R 'icheck {block}' /dev/sda1"
    # print(">> " + command)
    result_of_icheck = os.popen(command)
    # print(result_of_icheck)
    result_of_icheck = result_of_icheck.readlines()[-1]
    inode_temp = result_of_icheck.split()[-1]

    if inode_temp.isdigit():
        # find the directory
        inode = int(inode_temp)

        if inode == 8:
            # data_with_path = data_with_path + '\t' +"system reserved area(inode 8)\n"
            pass

        else:
            command = f"debugfs -R 'ncheck {inode}' /dev/sda1"
            # print(">>" + command)
            result_of_ncheck = os.popen(command).readlines()[-1]
            result_of_ncheck = result_of_ncheck.split()[-1]
            # print(result_of_ncheck)
            if UpperDir in result_of_ncheck:
                data_with_path += data[i][:-1]
                data_with_path = data_with_path + '\t' + result_of_ncheck + "\t[UpperLayer]" + '\n'
            else:
                for j in range(len(LowerDirList)):
                    if "init" in LowerDirList[j]:
                        pass
                    else:
                        if str(LowerDirList[j])[11:] in result_of_ncheck:
                            data_with_path += data[i][:-1]
                            data_with_path = data_with_path + '\t' + result_of_ncheck + "\t[LowerLayer]" + '\n'

    else:
        # data_with_path = data_with_path + '\t' +"directory not found\n"
        pass

    print("period: " + str(i) + " / " + str(len(data)))
    sys.stdout.flush()

# write the result in the new file "result_path.txt"
print("process finished")
final.write(data_with_path)
origin_file.close()
final.close()

