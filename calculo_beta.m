freqs = linspace(26,40,801)*1e9;
guide_len = 0.1;
fc = 21.077e9;
c = 299792458; 
lg = c./sqrt(freqs.^2-fc^2);
beta = (2*pi./lg)';
n_laps = 5;
wr28_corta = sparameters("PruebaWR28_larga.s2p");
beta_medida = (-unwrap(angle(squeeze(wr28_corta.Parameters(2,1,:))))+n_laps*2*pi)./guide_len;
figure(1);
plot(freqs/1e9,beta_medida);
hold on;
plot(freqs/1e9,beta);
legend(["Medido","Teorico"])
hold off;
figure(2);
title("Error")
plot(freqs/1e9,beta_medida-beta);

