filename_template = "med_switching_p_%d_channels_on_%d.s2p";
channels = ["Channel 0","Channel 1","Channel 2","Channel 3","Channel 4","Channel 5","Channel 6","Channel 7"];
for i = 1:8
    figure(i);
    for j = 0:7
        s_params = sparameters(sprintf(filename_template,j,i));
        freqs = s_params.Frequencies;
        s_params = s_params.Parameters;
        plot(freqs/1e9,20*log10(abs(squeeze(s_params(2,1,:)))),'LineWidth',1.2);
        if j == 0
            hold on;
        end
    end
    legend(channels);
    title(sprintf("Enabled ports %d",i));
    axis tight;
    grid minor;
    xlabel("Frequency (GHz)");
    ylabel("S21 (dB)");
    hold off;
end
