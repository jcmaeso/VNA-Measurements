channel = 4;
figure(1);
for i = 0:63
    sp = sparameters(sprintf("ch%d_amp%d.s2p",channel,i));
    toPrint = squeeze(20*log10(abs(sp.Parameters(2,1,:))));
    plot(sp.Frequencies/1e9,toPrint);
    if i == 0
        hold on;
    end
end

hold off;
figure(2)
for i = 0:63
    sp = sparameters(sprintf("ch%d_pha%d.s2p",channel,i));
    toPrint = squeeze(rad2deg(angle(sp.Parameters(2,1,:))));
    sp = sparameters(sprintf("ch%d_pha%d.s2p",channel,0));
    ref = squeeze(rad2deg(angle(sp.Parameters(2,1,:))));
    plot(sp.Frequencies/1e9,wrapTo360(toPrint-ref));
    if i == 0
        hold on;
    end
end

hold off;

%% Frecuencia 1.06GHz
f  = 1.06e9;
lambda = 3e8/f;

fases = -k*R*cosd(maxApun -index*distgrados);


