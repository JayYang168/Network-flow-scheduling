# Network-flow-scheduling
中兴捧月通用软件赛道网络流调度问题\
赛题链接:https://zte.hina.com/zte/software/desc
1 Flow 类\
--init方法：流属性，包含流id，流带宽，流到达实际，流发送时间和流开始发送时间。\
--inputPort方法：流进入端口，即flow开始发送,flow从端口开始发送需要满足两个条件1.port的剩余带宽大于等于flow的带宽2.port的仿真钟大于flow的进入时间。\
--getinfo 方法：获取流id,端口id和开始发送时间。\
2 Port类\
--init方法：端口属性，包含端口id,端口带宽，端口剩余带宽，端口中每个流离开的时间列表及其对应的流带宽，端口仿真钟即当前端口发送完某个流的时间，当端口初始为空时仿真钟为0，nextClock当前端口所有流中最先发送完毕的时间，用于仿真钟的推进。\
--outputflow方法:输出发送完毕的流，流从端口输出有两种情况\
		1.port带宽已满,等待队列未空\
    2.下一个flow的到达时间大于等于Port的仿真钟clock时间\
3 openflow 方法：读取流文件\
4 openport 方法：读取端口文件\
5 greedy算法:贪心算法将流分配给端口
