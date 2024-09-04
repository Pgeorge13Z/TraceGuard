function [time_each] = PseudoRandomStatic(time_each,Ntot)

% %Example of Bayesian Network using Bayes Net toolbox
% close all
% clear all
% clc

% %Number of clusters for the Bayesian Attack Graph
% Nclusters = 2;
% %Number of nodes per cluster
% N = 10;
%Total number of nodes in the Bayesian Attack Graph
% Ntot = 80;

sim_Count=5;
%Initialize the adjacency matrix
dag = zeros(Ntot,Ntot);


%Maximum number of parents allowed per node in the BAG
max_edges = 4;

sum_jt=0;
for c=1:sim_Count
%Create the adjacency matrix 生成最大父节点数为max_edges的矩阵
    dag = zeros(Ntot,Ntot);    
    for i = 2:Ntot
        dif = Ntot - 1 - (Ntot - i);
        rd = randi([1 max_edges],1,1); %生成1到max_edges的随机整数
        aux = 1:dif; 
        ind = randperm(dif); %将1到dif打乱随机排列
        aux = aux(ind);%将1到dif打乱随机排列
        dag(i, aux(1:min(rd,length(aux)))) = 1; %矩阵每一行随机选一或两个置为1
    end
    dag = dag';


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
    %If you want to add non-empty evidence (to perform dynamic analysis), just
%     if(evi==2)
%         evidence{1} = 2; %Set the node 1 to true (False = 1; True = 2)
%     elseif(evi==3)
%         evidence{1} = 2; %Set the node 1 to true (False = 1; True = 2)
%         evidence{2} = 2; %Set the node 1 to true (False = 1; True = 2)
%     elseif(evi==4)
%         evidence{1} = 2; %Set the node 1 to true (False = 1; True = 2)
%         evidence{2} = 2; %Set the node 1 to true (False = 1; True = 2)
%         evidence{3} = 2; %Set the node 1 to true (False = 1; True = 2)
%     end
    %Enter evidence
    [engine, loglik] = enter_evidence(engine, evidence);

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
end
fprintf('Avg. Inference time with JT, max_edges= %1.0f is %1.4f\n',max_edges,sum_jt/sim_Count);
time_each(1)=sum_jt/sim_Count;

