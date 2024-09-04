function [cpt] = createORtable(probs)

if (isempty(probs))
    %cpt = [0 1];
    cpt = [0.2 0.8];
else

    npa = length(probs);
    q = 1 - probs;
    cpt = zeros(2, 2^npa);

    %十进制转化为二进制，倒着写
    vals = dec2bin(0:(2^npa-1));

    for i=1:2^npa
        c = find(vals(i,:) == 1);
        cpt(1,i) = prod(q(c));
    end

    cpt(2,:) = 1 - cpt(1,:);
end

cpt = cpt';

end