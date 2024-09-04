x=100:100:1000;
y1=[0 1.4242 2.7121 8.2727 16.6061 23.2121 36.0909 49.2424 68.6667 100.3636];
c=polyfit(x,y1,2);
d=polyval(c,x,1)
y2=[0 0.6998 1.9363 6.1882 13.4556 23.7386 37.0370 53.3509 72.6803 95.0252]
y1=[0 0.08 0.17 0.26 0.35 0.44 0.53 0.62 0.71 0.8]
subplot(2,1,1)
plot(x,y2,'r'),axis([0 1100 0 120])
hold on;
plot(x,y2,'or'),axis([0 1100 0 120])
%xlabel('证据节点的数量');ylabel('推理时间');
%legend('static'),title('a.伪随机结构动态分析时间消耗'),

xlabel('Number of nodes');ylabel('Resoning time');
legend('static'),
subplot(2,1,2)
plot(x,y1,'b'),axis([0 1100 0 1])
hold on;
plot(x,y1,'ob'),axis([0 1100 0 1])
%xlabel('证据节点的数量');ylabel('推理时间');
%legend('dynamic'),title('b.伪随机结构静态分析时间消耗'),

xlabel('Number of nodes');ylabel('Resoning time');
legend('dynamic'),