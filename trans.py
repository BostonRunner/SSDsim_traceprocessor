##################################################################################
# Python script of handling the output of blkparse and add the path of file      #
# Please change the directory according to your system and device                #
# Author: Ruofei Wu                                                              #
# 10-28-2024                                                                     #
# Renewed in 09-30-2024                                                          #
##################################################################################


# open the log
origin_file = open("./results/result_path.txt", "r")
final = open("./results/io.ascii", "w")
cursor = 0
print("File reading")
# read the log
data = origin_file.readlines()
print("File processing")
# read the inode
data_with_path = ""
for i in range(len(data)):
    time = int(eval(data[i].split()[3]) * 1000000000)
    print(data[i].split())
    sector = int(eval(data[i].split()[12]))
    size = int(eval(data[i].split()[9]))
    layer = data[i].split()[-1]
    if time > cursor:
        is_lower_layer = -1
        if layer == "[UpperLayer]":
            is_lower_layer = 0
        elif layer == "[LowerLayer]":
            is_lower_layer = 1
        data_with_path = data_with_path + ' ' + str(time) + " 1 0 " + str(sector) + ' ' + str(size) + ' ' \
            + str(is_lower_layer) + '\n'
        cursor = 0
    else:
        continue


# write the result in the new file "result_path.txt"
print("process finished")
final.write(data_with_path)
origin_file.close()
final.close()

