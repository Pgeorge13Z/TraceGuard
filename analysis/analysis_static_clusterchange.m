%Example of PS and Cluster for static analysis
clear;
clc;

%总节点数
Ntot=80;
%总簇数，当簇数为1时为伪随机结构
Nclustersmax=20; 
%每一种结构的贝叶斯推理所需时间
time_each=zeros(1,Nclustersmax);

Nclsutersarray=1:Nclustersmax; %用于打印图的横轴

time_each=PseudoRandomStatic(time_each,Ntot);
time_each=Clusterstatic(time_each,Ntot,Nclustersmax);

plot(Nclsutersarray,time_each);title('Variation of inference time with structure in static analysis');
xlabel('Number of clusters');ylabel('time');

%ylim([0,0.5])

