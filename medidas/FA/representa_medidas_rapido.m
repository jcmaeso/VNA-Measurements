freq = linspace(27.5,31,51);
cnt = 0;
measurement = 0;
figure(1);
for i = 0:7
    sp = sparameters(sprintf("m_%d_p%d.s2p",measurement,i));
    plot(freq,20*log10(abs(squeeze(sp.Parameters(2,1,:)))))
    if cnt == 0
        hold on;
    end
    cnt = cnt+1;
end
hold off;
cnt = 0;
figure(2);
for i = 0:7
    sp = sparameters(sprintf("m_%d_p%d.s2p",measurement,0));
    sp1 = sparameters(sprintf("m_%d_p%d.s2p",measurement,i));
    pha0 = squeeze(rad2deg(angle(sp.Parameters(2,1,:))));
    pha1 = squeeze(rad2deg(angle(sp1.Parameters(2,1,:))));
    plot(freq,wrapTo360(pha1-pha0))
    if cnt == 0
        hold on;
    end
    cnt = cnt+1;
end
legend(["CH0","CH1","CH2","CH3","CH4","CH5","CH6","CH7"])
hold off;