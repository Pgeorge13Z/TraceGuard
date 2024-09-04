%Example of Bayesian Network using Bayes Net toolbox
close all
clear all
clc

%Number of clusters for the Bayesian Attack Graph
Nclusters = 4;
%Number of nodes per cluster
for N = 5:50
%Total number of nodes in the Bayesian Attack Graph
Ntot = Nclusters*N;
u=4;
sim_Count=5;
%Initialize the adjacency matrix
dag = zeros(Ntot,Ntot);

%Maximum number of parents allowed per node in the BAG
max_edges = u;

sum_jt=0;
sum_jt2=0;
for c=1:sim_Count
%Create the adjacency matrix 生成最大父节点数为max_edges的矩阵
for j=1:Nclusters
    dag2 = zeros(N,N);    
    for i = 2:N
        dif = N - 1 - (N - i);
        rd = randi([1 max_edges],1,1); %生成1到max_edges的随机整数
        aux = 1:dif; 
        ind = randperm(dif); %将1到dif打乱随机排列
        aux = aux(ind);%将1到dif打乱随机排列
        dag2(i, aux(1:min(rd,length(aux)))) = 1; %矩阵每一行随机选一或两个置为1
    end
    dag2 = dag2';
    dag(N*(j-1)+1:N*(j-1)+N,N*(j-1)+1:N*(j-1)+N) = dag2;
    c1 = 1:Ntot;
    c2 = N*(j-1)+1:N*(j-1)+N;
    c1 = setdiff(c1,c2); %返回原c1存在，c2中不存在的
    perm = randperm(length(c1));
    c1 = c1(perm);
    rd = randi([N*(j-1)+1,N*(j-1)+N]);
    %将两个簇结构连接
    if (rd > c1(1))
        dag(c1(1),rd) = 1;
    else
        dag(rd,c1(1)) = 1;
    end  
end


%All variables are Bernoulli random variables, so they have two states:
%True/False. This variable is used by BayesNet toolbox
node_sizes = 2*ones(1,Ntot); 

%Name of the nodes (in this case, to simplify, we just use the number of
%the node)
names = cell(1,Ntot);
for i=1:Ntot
    names{i} = num2str(i);
end

%Create the Bayesian network structure with Bayesnet
bnet = mk_bnet(dag, node_sizes, 'names', names, 'discrete', 1:Ntot);

%Probability of having AND-type conditional probability tables. Thus, the
%probability of having OR-type conditional probability tables is 1 - pAND
pAND = 0.2;

for i=1:Ntot
    npa = sum(dag(:,i));

    %Choose the type of conditional probability table (AND/OR) at random
    r = rand(1) > pAND;
    %Create OR conditional probability table
    if (r == 1)
        %We draw the probability from the distribution of CVSS scores
        probs = drawRandomCVSS(npa);
        cpt = createORtable(probs);
    %Create AND conditional probability table
    else
        %We draw the probability from the distribution of CVSS scores
        probs = drawRandomCVSS(npa);
        cpt = createANDtable(probs);
    end
    %Insert the conditional probability table into the Bayesnet object
    bnet.CPD{i} = tabular_CPD(bnet, i, cpt);
end


% %Show the graph
% bg = biograph(dag);
% bg.view;



%%  Inference with Junction Tree:
    tt = cputime;
    %Engine used for Junction Tree
    engine = jtree_inf_engine(bnet);
    %Vector to indicate the evidence
    evidence = cell(1,Ntot);
    [engine, ll] = enter_evidence(engine, evidence);
    %Vector to store the unconditional/posterior probabilities of the nodes in
    %the Bayesian network, i.e. p(X_i = True) or p(X_i = True | Evidence)
    pTrueJT = zeros(Ntot,1);
    %Compute the unconditional/posterior probabilities
    for i=1:Ntot
        marg = marginal_nodes(engine, i);
        pTrueJT(i) = marg.T(1);    
    end

    time_jt = cputime - tt;
    %disp('**************************************************');
    %fprintf('Inference time with Junction Tree %1.4f\n',time_jt);
    sum_jt = sum_jt + time_jt;
    
  %% dynamic inference
  tt=cputime;
  evidence{1} = 2;
  [engine, ll] = enter_evidence(engine, evidence);
      pTrueJT = zeros(Ntot,1);
    %Compute the unconditional/posterior probabilities
    for i=1:Ntot
        marg = marginal_nodes(engine, i);
        pTrueJT(i) = marg.T(1);    
    end
    sum_jt2 = cputime - tt;
end
sum_jt-sum_jt2
fprintf('Avg. Inference time with JT,N=%1.0f, u= %1.0f is %1.4f,Dynamictime=%1.4f\n',N,u,sum_jt/sim_Count,sum_jt2/sim_Count);
end
