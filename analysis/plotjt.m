x=10:10:90
y1=[0 0 0 0 0 0.2 1 2 6.5];
y2=[0 0 0 0 0.05 0.4 1.2 4.1 12];
c=polyfit(x,y1,2)
d=polyval(c,x,1)
e=polyfit(x,y2,2)
f=polyval(e,x,1)
y1=[0,0,0,0,0,0.5157,1.6850,3.2539,5.2224];
y1=[0.219,0.0437,0.0719,0.2281,0.1469,0.3688,1.3937,3.5813,8.2224]
y2=[0.1437 0.0781 0.1 0.2531 0.2062 0.3688 1.5562 5.8187 12];
plot(x,y1,'r',x,y2,'b'),axis([0 100 0 14])
hold on;
plot(x,y1,'or',x,y2,'ob'),axis([0 100 0 14])
%legend('dynamic','static'),title('伪随机结构静态分析与动态分析的对比'),
%xlabel('证据节点的数量');ylabel('推理时间');
legend('dynamic','static'),
xlabel('Number of summary nodes');ylabel('Reasoning time');