% Simulation of a continuous dynamic system described by ordinary
% differential equations.
%
% INITIAL SEGMENT
%
% Define constant model parameters as global variables. Set the initial 
% conditions of the states and set up the input to the model.
%
% It is good practice to clear the MATLAB workspace at the beginning of 
% a program

clearvars -except out

% Define and initialise the model input and any model parameters
% as global variables so that they can be read in the function model.m.

global BS Gc JM JW KC KD KE KH KS KT KV KY L R RM RW VD VT KI stepsize

% --- Mechanical and electrical parameters (Appendix A) ---
BS = 0.02;          % Damping coefficient [N·m/(rad/s)]
Gc = 2;          % Proportional controller gain
JM = 0.003;         % Motor armature inertia [kg·m^2]
JW = 0.001;         % Wheel inertia [kg·m^2]
KC = 1.2;           % Conditioning gain
KD = 18.14;         % Damping gain (yaw)
KE = 0.35;          % Back-emf constant [V·s/rad]
KH = 1.2;           % Heading sensor gain
KS = 9.81;          % Sway stiffness (velocity coupling)
KT = 0.35;          % Torque constant [N·m/A]
KV = 0.486;         % Velocity damping coefficient
KY = 29.94;         % Yaw stiffness (cross-coupling)
L  = 0.16;          % Motor inductance [H]
R  = 5.4;           % Motor resistance [Ω]
RM = 0.124;         % Moment arm [m]
RW = 0.064;         % Wheel radius [m]
VD = 3.0;           % Drive voltage [V]
VT = 0.75;          % Forward velocity [m/s]
KI = 1.0;

% Define parameters for the simulation

stepsize = 0.002;				% Integration step size
comminterval = 0.002;			% Communications interval
EndTime = 20;					% Duration of the simulation (final time)
i = 0;							% Initialise counter for data storage

% --- Initial conditions for the 9-state model ---
% [ iL  iR  wML  wMR  wWL  wWR  v   r   psi ]
x = [ 0;   % iL  - left motor current (A)
      0;   % iR  - right motor current (A)
      0;   % wML - left motor angular speed (rad/s)
      0;   % wMR - right motor angular speed (rad/s)
      0;   % wWL - left wheel angular speed (rad/s)
      0;   % wWR - right wheel angular speed (rad/s)
      0;   % v   - sway velocity (m/s)
      1;   % r   - yaw rate (rad/s)
     -12*pi/180;0] % psi - initial yaw angle (rad)

xdot = zeros(length(x),1); 

%
% END OF INITIAL SEGMENT - all parameters initialised
%
% DYNAMIC SEGMENT
%
% The DYNAMIC SECTION is the main section of a simulation program. This is
% evaluated for every time interval during the simulation. Therefore it is 
% an interative process.

for time = 0:stepsize:EndTime
   
    % store time state and state derivative data every communication interval
   
    if rem(time,comminterval)==0
      
        i = i+1;					% increment counter 
        tout(i) = time;	 	% store time
        xout(i,:) = x;			% store states
        xdout(i,:) = xdot;	% store state derivatives
      
    end							% end of storage      
   
    % CONTROL SECTION
    
    u = 55 * pi/180;   % reference yaw angle ψ_ref = 55° (converted to radians)

    % DERIVATIVE SECTION
	%
	% The DERIVATIVE SECTION contains the statements needed to evaluate the
	% state derivatives - these statements define the dynamic model (model.m)
	
	xdot = rover_state_space(x,u);

	% END OF DERIVATIVE SECTION
	%
	% INTEG SECTION
	% 
    % Numerical integration of the state derivatives for this time interval
   
    x = rk4int('rover_state_space', stepsize, x, u);    
   
    % END OF INTEG SECTION
   
end

% END OF DYNAMIC SEGMENT
%
% ==============================================================
%
% The TERMINAL SEGMENT contains statements that are executed after the simulation 
% is complete e.g. plotting results

figure('Name','Rover Turning Control System Responses','NumberTitle','off');
tdeg = 180/pi;   % radians → degrees

% === Bright and vivid color palette (no gray) ===
clrLeft   = [0.00 0.60 1.00];  % bright sky blue
clrRight  = [1.00 0.40 0.00];  % vivid orange
clrWheelL = [0.00 0.90 0.70];  % turquoise green
clrWheelR = [1.00 0.80 0.20];  % golden yellow
clrSway   = [0.70 0.20 1.00];  % violet
clrYaw    = [0.00 0.80 0.30];  % bright green
clrPsi    = [1.00 0.10 0.10];  % bright red (for yaw angle)
clrRef    = [0.00 0.80 0.30];  % pure black for ψ_ref line (neutral reference)

% --- 1. Motor & Wheel Speeds ---
subplot(3,2,1)
plot(tout, xout(:,3), '-',  'Color', clrLeft,   'LineWidth', 1.8); hold on
plot(tout, xout(:,4), '-',  'Color', clrRight,  'LineWidth', 1.8);
plot(tout, xout(:,5), '--', 'Color', clrWheelL, 'LineWidth', 1.4);
plot(tout, xout(:,6), '--', 'Color', clrWheelR, 'LineWidth', 1.4);
xlabel('Time [s]');
ylabel('\omega [rad/s]');
title('Motor and Wheel Speeds');
legend({'\omega_{ML}','\omega_{MR}','\omega_{WL}','\omega_{WR}'}, ...
       'Location','best');
grid on; box on;

% --- 2. Motor Currents ---
subplot(3,2,2)
plot(tout, xout(:,1), '-', 'Color', clrLeft,  'LineWidth', 1.8); hold on
plot(tout, xout(:,2), '-', 'Color', clrRight, 'LineWidth', 1.8);
xlabel('Time [s]');
ylabel('Current [A]');
title('Motor Currents');
legend({'i_L','i_R'},'Location','best');
grid on; box on;

% --- 3. Sway Velocity ---
subplot(3,2,3)
plot(tout, xout(:,7), '-', 'Color', clrSway, 'LineWidth', 1.8);
xlabel('Time [s]');
ylabel('v [m/s]');
title('Sway Velocity');
grid on; box on;

% --- 4. Yaw Rate ---
subplot(3,2,4)
plot(tout, xout(:,8), '-', 'Color', clrYaw, 'LineWidth', 1.8);
xlabel('Time [s]');
ylabel('r [rad/s]');
title('Yaw Rate');
grid on; box on;

% --- 5. Yaw Angle ---
subplot(3,2,[5 6])
plot(tout, xout(:,9)*tdeg, '-', 'Color', clrPsi, 'LineWidth', 2.0); hold on
yline(55, '--', 'Color', clrRef, 'LineWidth', 1.5, ...
    'Label', '\psi_{ref} = 55°', ...
    'LabelHorizontalAlignment', 'left', ...
    'LabelVerticalAlignment', 'bottom');
xlabel('Time [s]');
ylabel('\psi [deg]');
title('Yaw Angle Response');
grid on; box on;

% --- Overall title ---
sgtitle('Rover Turning Control System Simulation Results', 'FontWeight', 'bold');

%======================================================
%==================SIMULINK PLOTTING===================
% =====================================================

figure('Name','Rover Turning Control System Responses','NumberTitle','off');
tdeg = 180/pi;   % radians → degrees

% === Bright and vivid color palette (no gray) ===
clrLeft   = [0.00 0.60 1.00];  % bright sky blue
clrRight  = [1.00 0.40 0.00];  % vivid orange
clrWheelL = [0.00 0.90 0.70];  % turquoise green
clrWheelR = [1.00 0.80 0.20];  % golden yellow
clrSway   = [0.70 0.20 1.00];  % violet
clrYaw    = [0.00 0.80 0.30];  % bright green
clrPsi    = [1.00 0.10 0.10];  % bright red
clrRef    = [0.00 0.80 0.30];  % green for ψ_ref line

% ==============================================================
% Extract timeseries safely from the SimulationOutput
omega_ML_ts = out.('omega_ML_simulink');
omega_MR_ts = out.('omega_MR_simulink');
omega_WL_ts = out.('omega_WL_simulink');
omega_WR_ts = out.('omega_WR_simulink');
IL_ts       = out.('IL_simulink');
IR_ts       = out.('IR_simulink');
v_ts        = out.('v_simulink');
r_ts        = out.('r_simulink');
psi_ts      = out.('psi_simulink');

% ==============================================================
% Extract time and data arrays
t_omega_ML = omega_ML_ts.Time;   omega_ML = omega_ML_ts.Data;
t_omega_MR = omega_MR_ts.Time;   omega_MR = omega_MR_ts.Data;
t_omega_WL = omega_WL_ts.Time;   omega_WL = omega_WL_ts.Data;
t_omega_WR = omega_WR_ts.Time;   omega_WR = omega_WR_ts.Data;
t_IL       = IL_ts.Time;         IL       = IL_ts.Data;
t_IR       = IR_ts.Time;         IR       = IR_ts.Data;
t_v        = v_ts.Time;          v        = v_ts.Data;
t_r        = r_ts.Time;          r        = r_ts.Data;
t_psi      = psi_ts.Time;        psi      = psi_ts.Data;

% ==============================================================
% 1. Motor & Wheel Speeds
subplot(3,2,1)
plot(t_omega_ML, omega_ML, '-',  'Color', clrLeft,   'LineWidth', 1.8); hold on
plot(t_omega_MR, omega_MR, '-',  'Color', clrRight,  'LineWidth', 1.8);
plot(t_omega_WL, omega_WL, '--', 'Color', clrWheelL, 'LineWidth', 1.4);
plot(t_omega_WR, omega_WR, '--', 'Color', clrWheelR, 'LineWidth', 1.4);
xlabel('Time [s]');
ylabel('\omega [rad/s]');
title('Motor and Wheel Speeds');
legend({'\omega_{ML}','\omega_{MR}','\omega_{WL}','\omega_{WR}'}, 'Location','best');
grid on; box on;

% ==============================================================
% 2. Motor Currents
subplot(3,2,2)
plot(t_IL, IL, '-', 'Color', clrLeft,  'LineWidth', 1.8); hold on
plot(t_IR, IR, '-', 'Color', clrRight, 'LineWidth', 1.8);
xlabel('Time [s]');
ylabel('Current [A]');
title('Motor Currents');
legend({'i_L','i_R'},'Location','best');
grid on; box on;

% ==============================================================
% 3. Sway Velocity
subplot(3,2,3)
plot(t_v, v, '-', 'Color', clrSway, 'LineWidth', 1.8);
xlabel('Time [s]');
ylabel('v [m/s]');
title('Sway Velocity');
grid on; box on;

% ==============================================================
% 4. Yaw Rate
subplot(3,2,4)
plot(t_r, r, '-', 'Color', clrYaw, 'LineWidth', 1.8);
xlabel('Time [s]');
ylabel('r [rad/s]');
title('Yaw Rate');
grid on; box on;

% ==============================================================
% 5. Yaw Angle
subplot(3,2,[5 6])
plot(t_psi, psi*tdeg, '-', 'Color', clrPsi, 'LineWidth', 2.0); hold on
yline(55, '--', 'Color', clrRef, 'LineWidth', 1.5, ...
    'Label', '\psi_{ref} = 55°', ...
    'LabelHorizontalAlignment', 'left', ...
    'LabelVerticalAlignment', 'bottom');
xlabel('Time [s]');
ylabel('\psi [deg]');
title('Yaw Angle Response');
grid on; box on;

% ==============================================================
% Overall title
sgtitle('Rover Turning Control System Simulation Results - SIMULINK', ...
        'FontWeight', 'bold');

% ==============================================================

%% ==============================================================
%% COMBINED COMPARISON PLOTS – MATLAB vs SIMULINK
%% ==============================================================

figure('Name','Rover Turning Control System Responses - COMBINED','NumberTitle','off');
tdeg = 180/pi;   % radians → degrees

% === Bright color palette (consistent with previous figures) ===
clrLeft   = [0.00 0.60 1.00];  % bright sky blue
clrRight  = [1.00 0.40 0.00];  % vivid orange
clrWheelL = [0.00 0.90 0.70];  % turquoise green
clrWheelR = [1.00 0.80 0.20];  % golden yellow
clrSway   = [0.70 0.20 1.00];  % violet
clrYaw    = [0.00 0.80 0.30];  % bright green
clrPsi    = [1.00 0.10 0.10];  % bright red
clrRef    = [0.00 0.80 0.30];  % green for ψ_ref line

% ==============================================================
% 1. Motor & Wheel Speeds
subplot(3,2,1)
% MATLAB model (solid)
plot(tout, xout(:,3), '-', 'Color', clrLeft,  'LineWidth', 1.6); hold on
plot(tout, xout(:,4), '-', 'Color', clrRight, 'LineWidth', 1.6);
plot(tout, xout(:,5), '--', 'Color', clrWheelL, 'LineWidth', 1.2);
plot(tout, xout(:,6), '--', 'Color', clrWheelR, 'LineWidth', 1.2);
% Simulink (dashed, slightly thinner)
plot(t_omega_ML, omega_ML, ':', 'Color', clrLeft,  'LineWidth', 1.6);
plot(t_omega_MR, omega_MR, ':', 'Color', clrRight, 'LineWidth', 1.6);
plot(t_omega_WL, omega_WL, '-.', 'Color', clrWheelL, 'LineWidth', 1.3);
plot(t_omega_WR, omega_WR, '-.', 'Color', clrWheelR, 'LineWidth', 1.3);
xlabel('Time [s]');
ylabel('\omega [rad/s]');
title('Motor and Wheel Speeds (MATLAB vs Simulink)');
legend({'\omega_{ML}','\omega_{MR}','\omega_{WL}','\omega_{WR}', ...
        '\omega_{ML}^{sim}','\omega_{MR}^{sim}','\omega_{WL}^{sim}','\omega_{WR}^{sim}'}, ...
        'Location','best','FontSize',8);
grid on; box on;

% ==============================================================
% 2. Motor Currents
subplot(3,2,2)
plot(tout, xout(:,1), '-', 'Color', clrLeft, 'LineWidth', 1.8); hold on
plot(tout, xout(:,2), '-', 'Color', clrRight, 'LineWidth', 1.8);
plot(t_IL, IL, ':', 'Color', clrLeft, 'LineWidth', 1.6);
plot(t_IR, IR, ':', 'Color', clrRight, 'LineWidth', 1.6);
xlabel('Time [s]');
ylabel('Current [A]');
title('Motor Currents (MATLAB vs Simulink)');
legend({'i_L','i_R','i_L^{sim}','i_R^{sim}'},'Location','best','FontSize',8);
grid on; box on;

% ==============================================================
% 3. Sway Velocity
subplot(3,2,3)
plot(tout, xout(:,7), '-', 'Color', clrSway, 'LineWidth', 1.8); hold on
plot(t_v, v, ':', 'Color', clrSway, 'LineWidth', 1.6);
xlabel('Time [s]');
ylabel('v [m/s]');
title('Sway Velocity (MATLAB vs Simulink)');
legend({'v','v^{sim}'},'Location','best','FontSize',8);
grid on; box on;

% ==============================================================
% 4. Yaw Rate
subplot(3,2,4)
plot(tout, xout(:,8), '-', 'Color', clrYaw, 'LineWidth', 1.8); hold on
plot(t_r, r, ':', 'Color', clrYaw, 'LineWidth', 1.6);
xlabel('Time [s]');
ylabel('r [rad/s]');
title('Yaw Rate (MATLAB vs Simulink)');
legend({'r','r^{sim}'},'Location','best','FontSize',8);
grid on; box on;

% ==============================================================
% 5. Yaw Angle
subplot(3,2,[5 6])
plot(tout, xout(:,9)*tdeg, '-', 'Color', clrPsi, 'LineWidth', 2.0); hold on
plot(t_psi, psi*tdeg, ':', 'Color', clrPsi, 'LineWidth', 2.0);
yline(55, '--', 'Color', clrRef, 'LineWidth', 1.5, ...
    'Label', '\psi_{ref} = 55°', ...
    'LabelHorizontalAlignment', 'left', ...
    'LabelVerticalAlignment', 'bottom');
xlabel('Time [s]');
ylabel('\psi [deg]');
title('Yaw Angle (MATLAB vs Simulink)');
legend({'\psi','\psi^{sim}','\psi_{ref}'},'Location','best','FontSize',8);
grid on; box on;

% ==============================================================
% Overall title
sgtitle('Rover Turning Control System Responses - COMBINED MATLAB vs SIMULINK', ...
        'FontWeight','bold');


% END OF SIMULATION PROGRAM