clc;
clear;
close all;

filename_template = "med_switching_p_%d_channels_on_%d.s2p";
channels = ["Channel 0","Channel 1","Channel 2","Channel 3","Channel 4","Channel 5","Channel 6","Channel 7"];

%First we find nearest frequency in the sparameters frequency axis
freqs_to_evaluate = [17.7 18.95 20.2];
s_params_cst = zeros(3,8,8); %Frequency-State-Channel
test_sparams = sparameters(sprintf(filename_template,0,1));
for i = 1:length(freqs_to_evaluate)
    [~,index] = min(abs(freqs_to_evaluate(i)-test_sparams.Frequencies/1e9));
    freqs_to_evaluate(i) = index;
end
%Plot amplitude comparation and find desired values
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
        %Add Sparameter to matrix
        for k = 1:length(freqs_to_evaluate)
            s_params_cst(k,j+1,i) = s_params(2,1,freqs_to_evaluate(k));
        end
    end
    legend(channels);
    title(sprintf("Enabled ports %d",i));
    axis tight;
    grid minor;
    axis([17.5 21.4 -60 10]);
    xlabel("Frequency (GHz)")
    ylabel("S21 (dB)")
    hold off;
end

%Build Excel with the info
s_params_cst_mod = abs(s_params_cst);
s_params_cst_phase = wrapTo360(rad2deg(angle(s_params_cst)));
excel_params = zeros(8,8,2);
for i = 1:8
    %Normalization
     s_params_cst_mod(2,:,i) = s_params_cst_mod(2,:,i)./max(s_params_cst_mod(2,:,i));
     s_params_cst_phase(2,:,i) = s_params_cst_phase(2,:,i)-min(s_params_cst_phase(2,:,i));
    for j = 1:8
        excel_params(j,i,1) = s_params_cst_mod(2,j,i);
        excel_params(j,i,2) = s_params_cst_phase(2,j,i);
    end
end
excel_params = reshape(excel_params(:,:,:),8,16);
writematrix(excel_params,'CSTCombines.xlsx');