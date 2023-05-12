import os
import random
class Flow:
    def __init__(self,id,bandwidth,arriveT,sendT):
        self.id = id                             #流id
        self.bandwidth = bandwidth               #流带宽
        self.arriveT = arriveT                   #流到达时间
        self.sendT = sendT                       #流发送时间
        self.Startsendingtime = arriveT          #流开始发送时间
        self.portId = None

    def inputPort(self,port):
        '''流进入端口，即flow开始发送
        什么时候flow可以进入port？
        1.port的剩余带宽大于等于flow的带宽
        2.port的仿真钟大于flow的进入时间
        flow: Flow类
        clock:仿真钟,由port出去的flow的时间为准
        '''
        self.portId = port.id
        port.flowsBandwidth.append(self.bandwidth)
        port.leftBandwidth -= self.bandwidth #减去流带宽
        self.Startsendingtime = max(self.arriveT,port.clock)
        dt = self.Startsendingtime + self.sendT #flow的离开时间
        port.flowsDepart.append(dt)
        port.nextClock = min(port.nextClock,dt) #更新最早弹出时间
    
    def getinfo(self):
        '''流id,流带宽,流到达时间,流开始发送时间,流发送时间,流完成时间'''
        # return [self.id,self.bandwidth,self.arriveT,self.Startsendingtime,self.sendT,self.Completiontime]
        #流id,端口id,开始发送时间
        # temp = [str(self.id),str(self.portId),str(self.Startsendingtime)]
        # return ','.join(temp)
        return '{},{},{}'.format(self.id,self.portId,self.Startsendingtime)

class Port:
    def __init__(self,id,bandwidth):
        self.id = id
        self.bandwidth = bandwidth
        self.leftBandwidth = self.bandwidth #剩余带宽
        self.flowsDepart = []               #存放flow离开的时间
        self.flowsBandwidth = []            #存放Port中flow的带宽
        self.clock = 0                      #初始化仿真钟
        self.nextClock = float('inf')       #Port最早弹出时间
    
    def outputflow(self):
        '''流输出端口，输出已经完成传送的流
        什么时候输出？
        1.port带宽已满,等待队列未空
        2.下一个flow的到达时间大于等于Port的仿真钟clock时间
        '''
        
        idxs = []
        for idx in range(len(self.flowsDepart)):
            if self.nextClock == self.flowsDepart[idx]:
                idxs.append(idx)
        idxs.reverse()
        for idx in idxs:
            self.flowsDepart.pop(idx)
            self.leftBandwidth += self.flowsBandwidth.pop(idx)
            
        self.clock = self.nextClock 
        if len(self.flowsDepart) > 0:
            self.nextClock = min(self.flowsDepart)
        else:
            self.nextClock = self.clock
            
def openflow(flow_file):
    flows = []
    f = open(flow_file,encoding='utf-8')
    f_data = f.readlines()[1:]
    for row in f_data:
        id,bandwidth,arriveT,sendT = row.strip().split(',')
        flows.append(Flow(id,int(bandwidth),int(arriveT),int(sendT)))
    return flows

def openport(port_file):
    ports = []
    f = open(port_file,encoding='utf-8')
    f_data = f.readlines()[1:]
    for row in f_data:
        id,bandwidth = row.strip().split(',')
        ports.append(Port(id,int(bandwidth)))
    return ports



def greedy(file_root):
    ### 文件读取 ###
    flow_filename = os.path.join(file_root,'flow.txt')
    port_filename = os.path.join(file_root,'port.txt')
    result_filename = os.path.join(root,'result.txt')
    flows = openflow(flow_filename)#流id,流带宽，起始时间，发送时间
    ports = openport(port_filename)#端口id,端口带宽
    ### 数据预处理 ###
    # 按流的起始时间排序,等待队列
    # flows.sort(key=(lambda flow: (flow.arriveT * flow.bandwidth/(flow.sendT**2))),reverse=False) #2比较好
    flows.sort(key=(lambda flow: (flow.arriveT * flow.bandwidth/(flow.sendT**3))),reverse=False) #这个是最好的

    portsList = [port.bandwidth for port in ports]
    portsBandwidth = sorted(list(set(portsList)))
    portsDict = {bandwidth:[] for bandwidth in portsBandwidth} #丢弃区
    for bandwidth in portsBandwidth:
        for i,curbandwidth in enumerate(portsList):
            if curbandwidth >= bandwidth:
                portsDict[bandwidth].append(i)
    

    f = open(result_filename,'w',encoding='utf-8')
    threshold = len(ports) * 20#20的时候为30.1
    while len(flows) > 0:
        # 每装进去一个就更新时间
        waitList = flows.copy()
        ports.sort(key=(lambda port:(port.clock,1/(1+port.leftBandwidth))),reverse=False)
        curleftFlow = []
        for i,flow in enumerate(waitList):
            flag = False
            for port in ports:
                if flow.bandwidth <= port.leftBandwidth:
                    flow.inputPort(port)
                    flows.remove(flow)
                    f.write(flow.getinfo()+'\n')
                    flag = True
                    break
            if not flag:
                curleftFlow.extend(waitList[i:])
                break
                
                # count += 1
                # if count == threshold:
                #     curleftFlow.extend(waitList[i:])
                #     break
                # else:
                #     curleftFlow.append(flow)
        
        
        # 二阶段要丢掉一部分流
        waitListNum = len(curleftFlow)
        if  waitListNum > 0:
            if waitListNum > threshold:
                curleftFlow.sort(key=(lambda flow:flow.sendT * flow.bandwidth),reverse=True)
            while waitListNum > threshold:
                flow = curleftFlow.pop()
                for bandwidth,portsids in portsDict.items():
                    if bandwidth >= flow.bandwidth:
                        flow.portId = random.choice(portsids)
                        break
                flows.remove(flow)
                f.write(flow.getinfo()+'\n')
                waitListNum -= 1
            # 只将未空的port 按时间弹出，则按弹出时间来
            ports.sort(key=(lambda port:port.nextClock),reverse=False)
            portsClockDict = {}
            for port in ports:
                if port.nextClock not in portsClockDict.keys():
                    portsClockDict[port.nextClock] = [port]
                else:
                    portsClockDict[port.nextClock].append(port)
            ports.clear()
            flag = False
            for nextClock,tmpPorts in portsClockDict.items():
                if not flag:
                    for port in tmpPorts:
                        if len(port.flowsDepart) > 0:
                            port.outputflow()
                            flag = True

                ports.extend(tmpPorts)
          
    f.close()





if __name__ == '__main__':
    path = r"../data"
    files = os.listdir(path)
    for i,file in enumerate(files):
        root = os.path.join(path,file)
        greedy(root)

   


