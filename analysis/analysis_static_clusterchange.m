%Example of PS and Cluster for static analysis
clear;
clc;

%�ܽڵ���
Ntot=80;
%�ܴ�����������Ϊ1ʱΪα����ṹ
Nclustersmax=20; 
%ÿһ�ֽṹ�ı�Ҷ˹��������ʱ��
time_each=zeros(1,Nclustersmax);

Nclsutersarray=1:Nclustersmax; %���ڴ�ӡͼ�ĺ���

time_each=PseudoRandomStatic(time_each,Ntot);
time_each=Clusterstatic(time_each,Ntot,Nclustersmax);

plot(Nclsutersarray,time_each);title('Variation of inference time with structure in static analysis');
xlabel('Number of clusters');ylabel('time');

%ylim([0,0.5])

