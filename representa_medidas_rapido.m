freq = linspace(27.5,31.5,801);
cnt = 0;
figure(1);
for i = 0:3
    sp = sparameters(sprintf("m_%d_p%d.s2p",i,0));
    plot(freq,20*log10(abs(squeeze(sp.Parameters(2,1,:)))))
    if cnt == 0
        hold on;
    end
end
hold off;
cnt = 0;
figure(1);
for i = 1:3
    sp = sparameters(sprintf("m_%d_p%d.s2p",0,0));
    sp1 = sparameters(sprintf("m_%d_p%d.s2p",i,0));
    pha0 = squeeze(rad2deg(angle(sp.Parameters(2,1,:))));
    pha1 = squeeze(rad2deg(angle(sp1.Parameters(2,1,:))));
    plot(freq,pha1-pha0)
    if cnt == 0
        hold on;
    end
end
hold off;