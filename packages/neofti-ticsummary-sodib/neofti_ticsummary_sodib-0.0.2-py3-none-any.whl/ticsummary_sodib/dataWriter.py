from ticsummary_sodib.handlerData import *

def writeData(fileName,data:ProcessedData):
    with open(fileName,'w') as fp:
        fp.write("ch1;ch2;ch3;ch4;ch5;ch6;ch7;ch8;ch9;ch10;ch11;ch12;ch13;ch14;ch15;ch16;Time;Intensity;scCenter;scRightUp;scRightBottom;scLeftUp;scLeftBottom;Projection")
        fp.write('\n')
        listStr = list()
        intensity = np.sum(data.mcp,axis=1)
        projection = np.transpose(data.mcp).sum(axis=1)
        checkList = lambda i: listStr.append("")  if  i >= len(listStr) else None
        for i in range(0,len(data.mcp)):
            checkList(i)
            for item in data.mcp[i]:
                listStr[i] = listStr[i] + "{0};".format(item)
        for i in range(0,len(data.mcp)):
            listStr[i] = listStr[i] + "{0};".format(data.time[i])
        for i in range(0,len(data.mcp)):
            listStr[i] = listStr[i] + "{0};".format(intensity[i])
        for i in range(0,len(data.mcp)):
            listStr[i] = listStr[i] + "{0};".format(data.scCenter[i])
        for i in range(0,len(data.mcp)):
            listStr[i] = listStr[i] + "{0};".format(data.scRightUp[i])
        for i in range(0,len(data.mcp)):
            listStr[i] = listStr[i] + "{0};".format(data.scRightBottom[i])
        for i in range(0,len(data.mcp)):
            listStr[i] = listStr[i] + "{0};".format(data.scLeftUp[i])
        for i in range(0,len(data.mcp)):
            listStr[i] = listStr[i] + "{0};".format(data.scLeftBottom[i])
        for i in range(0,16):
            listStr[i] = listStr[i] + "{0};".format(projection[i])
        for item in listStr:
            fp.write(item)
            fp.write('\n')