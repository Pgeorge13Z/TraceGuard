%Example of PS and Cluster for static analysis
clear;
clc;

%总节点数
Ntot=75;
%总簇数，当簇数为1时为伪随机结构
Nclustersmax=20;
%每一种结构的贝叶斯推理所需时间
time_each=zeros(1,Nclustersmax);

Nclsutersarray=1:Nclustersmax; %用于打印图的横轴

time_each=PseudoRandomStatic(time_each,Ntot);
time_each=Clustersdynamic(time_each,Ntot,Nclustersmax);

plot(Nclsutersarray,time_each);title('Variation of inference time with structure in dynamic analysis');
xlabel('number of cluster ');ylabel('time');


