%% Buck Converter modelini kuran script (add_block/add_line ile)
mdl = 'BuckConverterModel_v2';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

%% --- Parametreler ---
Vin_val = 12;
Vout_target = 5;
D       = Vout_target / Vin_val;   % 0.4167
f_sw    = 100000;                  % 100 kHz
L_val   = 100e-6;
C_val   = 220e-6;
R_val   = 5;

Tsim    = 0.05;   % Simülasyon süresi (s)
MaxStep = 1/f_sw/50;

%% --- Model ayarları ---
set_param(mdl,'Solver','ode23t');
set_param(mdl,'StopTime',num2str(Tsim));
set_param(mdl,'MaxStep',num2str(MaxStep));

%% --- Bloklar ---
add_block('simulink/Sources/Constant', [mdl '/Vin'], ...
    'Value', num2str(Vin_val), 'Position',[40 40 80 60]);

add_block('simulink/Sources/Pulse Generator', [mdl '/PWM'], ...
    'Amplitude','1', 'Period', num2str(1/f_sw), ...
    'PulseWidth', num2str(D*100), ...
    'Position',[40 100 80 130]);

add_block('simulink/Math Operations/Product', [mdl '/Product1'], ...
    'Position',[140 60 180 100]);

add_block('simulink/Math Operations/Sum', [mdl '/Sum1'], ...
    'Inputs','+-', 'Position',[240 60 280 100]);

add_block('simulink/Math Operations/Gain', [mdl '/Gain_1_L'], ...
    'Gain', num2str(1/L_val), 'Position',[340 60 380 100]);

add_block('simulink/Continuous/Integrator', [mdl '/Integrator_iL'], ...
    'Position',[440 60 480 100]);

add_block('simulink/Math Operations/Sum', [mdl '/Sum2'], ...
    'Inputs','+-', 'Position',[540 60 580 100]);

add_block('simulink/Math Operations/Gain', [mdl '/Gain_1_C'], ...
    'Gain', num2str(1/C_val), 'Position',[640 60 680 100]);

add_block('simulink/Continuous/Integrator', [mdl '/Integrator_Vout'], ...
    'Position',[740 60 780 100]);

add_block('simulink/Math Operations/Gain', [mdl '/Gain_1_R'], ...
    'Gain', num2str(1/R_val), 'Position',[740 200 780 240]);

add_block('simulink/Sinks/Scope', [mdl '/Scope_iL'], 'Position',[540 260 580 290]);
add_block('simulink/Sinks/Scope', [mdl '/Scope_Vout'], 'Position',[840 60 880 100]);

add_block('simulink/Sinks/To Workspace', [mdl '/ToWS_iL'], ...
    'VariableName','iL_log','SaveFormat','Structure With Time', ...
    'Position',[540 320 620 350]);
add_block('simulink/Sinks/To Workspace', [mdl '/ToWS_Vout'], ...
    'VariableName','Vout_log','SaveFormat','Structure With Time', ...
    'Position',[840 320 920 350]);

%% --- Bağlantılar ---
add_line(mdl,'Vin/1','Product1/1');
add_line(mdl,'PWM/1','Product1/2');
add_line(mdl,'Product1/1','Sum1/1');
add_line(mdl,'Sum1/1','Gain_1_L/1');
add_line(mdl,'Gain_1_L/1','Integrator_iL/1');
add_line(mdl,'Integrator_iL/1','Sum2/1');
add_line(mdl,'Integrator_iL/1','Scope_iL/1','autorouting','on');
add_line(mdl,'Integrator_iL/1','ToWS_iL/1','autorouting','on');
add_line(mdl,'Sum2/1','Gain_1_C/1');
add_line(mdl,'Gain_1_C/1','Integrator_Vout/1');
add_line(mdl,'Integrator_Vout/1','Sum1/2','autorouting','on');
add_line(mdl,'Integrator_Vout/1','Gain_1_R/1','autorouting','on');
add_line(mdl,'Gain_1_R/1','Sum2/2','autorouting','on');
add_line(mdl,'Integrator_Vout/1','Scope_Vout/1','autorouting','on');
add_line(mdl,'Integrator_Vout/1','ToWS_Vout/1','autorouting','on');

save_system(mdl);
disp('Model kuruldu. Simüle etmek için: out = sim(mdl);');

%% --- Simüle et ---
out = sim(mdl);
Vout_log = out.Vout_log;
iL_log   = out.iL_log;

%% --- Sonucu geniş kapsamda incele ---
figure('Name','Buck Converter - Sonuc');

subplot(2,1,1);
plot(Vout_log.time, Vout_log.signals.values, 'LineWidth',1.2);
grid on; xlabel('t (s)'); ylabel('Vout (V)');
title(sprintf('Vout  (hedef = %.2f V)', Vout_target));

subplot(2,1,2);
plot(iL_log.time, iL_log.signals.values, 'LineWidth',1.2);
grid on; xlabel('t (s)'); ylabel('iL (A)');
title('İndüktör akımı');

%% --- Kararlı durum kontrolü (son %20'lik pencere) ---
tv = Vout_log.time; vv = Vout_log.signals.values;
w  = tv > 0.8*tv(end);
fprintf('Vout_ss ortalama = %.4f V, ripple(pp) = %.2f mV\n', ...
    mean(vv(w)), 1e3*(max(vv(w))-min(vv(w))));

ti = iL_log.time; vi = iL_log.signals.values;
wi = ti > 0.8*ti(end);
fprintf('iL_ss ortalama = %.4f A, ripple(pp) = %.3f A\n', ...
    mean(vi(wi)), max(vi(wi))-min(vi(wi)));