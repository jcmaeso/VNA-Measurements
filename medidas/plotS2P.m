clc;
clear;
close all;

directory = "Medidas TX3 Control Nuestro";
filename_template = "P%d_single_phase_0_amp_63.s2p";
channels = ["Channel 0","Channel 1","Channel 2","Channel 3","Channel 4","Channel 5","Channel 6","Channel 7"];
fig_title = "Medida con ";
figure;
for i = 0:7
    s_params = sparameters(fullfile(directory,sprintf(filename_template,i)));
    s_params = s_params.Parameters;
    plot(linspace(25,35,801),20*log10(abs(squeeze(s_params(2,1,:)))),'LineWidth',1.2);
    if i == 0
        hold on;
    end
end
legend(channels,'Location','northeast');
xlabel("Frequency (GHz)");
ylabel("S21 (dB)");
axis([25,35,-10 15]);
grid on;
grid minor;
title(fig_title)
