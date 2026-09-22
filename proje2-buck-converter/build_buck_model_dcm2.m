%% Buck Converter - CCM vs DCM Karsilastirmasi (Asama 2)
mdl = 'BuckConverterModel_DCM';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

%% --- Sabit parametreler ---
Vin_val = 12;
Vout_target = 5;
D       = Vout_target / Vin_val;
f_sw    = 100000;
L_val   = 100e-6;
C_val   = 220e-6;
Tsim    = 0.02;

R_kritik = 2*L_val*f_sw/(1-D);
fprintf('R_kritik = %.2f Ohm\n', R_kritik);

set_param(mdl,'Solver','ode45');
set_param(mdl,'StopTime',num2str(Tsim));
set_param(mdl,'MaxStep','auto');

%% --- Bloklar (Integrator_iL'ye diyot kisiti eklendi) ---
add_block('simulink/Sources/Constant', [mdl '/Vin'], 'Value', num2str(Vin_val), 'Position',[40 40 80 60]);
add_block('simulink/Sources/Pulse Generator', [mdl '/PWM'], 'Amplitude','1', 'Period', num2str(1/f_sw), 'PulseWidth', num2str(D*100), 'Position',[40 100 80 130]);
add_block('simulink/Math Operations/Product', [mdl '/Product1'], 'Position',[140 60 180 100]);
add_block('simulink/Math Operations/Sum', [mdl '/Sum1'], 'Inputs','+-', 'Position',[240 60 280 100]);
add_block('simulink/Math Operations/Gain', [mdl '/Gain_1_L'], 'Gain', num2str(1/L_val), 'Position',[340 60 380 100]);
add_block('simulink/Continuous/Integrator', [mdl '/Integrator_iL'], 'LimitOutput','on', 'LowerSaturationLimit','0', 'Position',[440 60 480 100]);
add_block('simulink/Math Operations/Sum', [mdl '/Sum2'], 'Inputs','+-', 'Position',[540 60 580 100]);
add_block('simulink/Math Operations/Gain', [mdl '/Gain_1_C'], 'Gain', num2str(1/C_val), 'Position',[640 60 680 100]);
add_block('simulink/Continuous/Integrator', [mdl '/Integrator_Vout'], 'Position',[740 60 780 100]);
add_block('simulink/Math Operations/Gain', [mdl '/Gain_1_R'], 'Gain', '0.2', 'Position',[740 200 780 240]);
add_block('simulink/Sinks/To Workspace', [mdl '/ToWS_iL'], 'VariableName','iL_log','SaveFormat','Structure With Time', 'Position',[540 320 620 350]);
add_block('simulink/Sinks/To Workspace', [mdl '/ToWS_Vout'], 'VariableName','Vout_log','SaveFormat','Structure With Time', 'Position',[840 320 920 350]);

%% --- Baglantilar ---
add_line(mdl,'Vin/1','Product1/1');
add_line(mdl,'PWM/1','Product1/2');
add_line(mdl,'Product1/1','Sum1/1');
add_line(mdl,'Sum1/1','Gain_1_L/1');
add_line(mdl,'Gain_1_L/1','Integrator_iL/1');
add_line(mdl,'Integrator_iL/1','Sum2/1');
add_line(mdl,'Integrator_iL/1','ToWS_iL/1','autorouting','on');
add_line(mdl,'Sum2/1','Gain_1_C/1');
add_line(mdl,'Gain_1_C/1','Integrator_Vout/1');
add_line(mdl,'Integrator_Vout/1','Sum1/2','autorouting','on');
add_line(mdl,'Integrator_Vout/1','Gain_1_R/1','autorouting','on');
add_line(mdl,'Gain_1_R/1','Sum2/2','autorouting','on');
add_line(mdl,'Integrator_Vout/1','ToWS_Vout/1','autorouting','on');

save_system(mdl);
disp('Model kuruldu (diyot kisitli).');

%% --- Iki yukle calistir: CCM (R=5) ve DCM (R=100) ---
R_list = [5, 100];
labels = {'CCM (R=5 Ohm)','DCM (R=100 Ohm)'};
results = struct();

for k = 1:numel(R_list)
    fprintf('Simule ediliyor: R = %d Ohm ...\n', R_list(k));
    set_param([mdl '/Gain_1_R'], 'Gain', num2str(1/R_list(k)));
    out = sim(mdl);
    results(k).Vout = out.Vout_log;
    results(k).iL   = out.iL_log;
end
disp('Tum simulasyonlar tamamlandi.');

%% --- Karsilastirma grafigi ---
figure('Name','CCM vs DCM Karsilastirma');
colors = {'b','r'};
for k = 1:2
    subplot(2,1,1); hold on;
    plot(results(k).Vout.time, results(k).Vout.signals.values, colors{k}, 'LineWidth',1.2);
    subplot(2,1,2); hold on;
    plot(results(k).iL.time, results(k).iL.signals.values, colors{k}, 'LineWidth',1.2);
end
subplot(2,1,1); grid on; xlabel('t (s)'); ylabel('Vout (V)');
title('Vout: CCM vs DCM'); legend(labels);
subplot(2,1,2); grid on; xlabel('t (s)'); ylabel('iL (A)');
title('iL: CCM vs DCM'); legend(labels);

%% --- Sayisal karsilastirma ---
for k = 1:2
    tv = results(k).Vout.time; vv = results(k).Vout.signals.values;
    w = tv > 0.8*tv(end);
    ti = results(k).iL.time; vi = results(k).iL.signals.values;
    wi = ti > 0.8*ti(end);
    fprintf('%s: Vout_ss=%.3f V, iL_ss=%.3f A, iL_min=%.3f A\n', labels{k}, mean(vv(w)), mean(vi(wi)), min(vi(wi)));
end
 