% ==============================================================
%   ROVER YAW SIMULATION WITH ERROR INTEGRATOR + KI SWEEP
% ==============================================================

clearvars -except out

global BS Gc JM JW KC KD KE KH KS KT KV KY L R RM RW VD VT KI 

% --- Mechanical and electrical parameters ---
BS = 0.02;
Gc = 5.0;          % fixed Gc
JM = 0.003;
JW = 0.001;
KC = 1.2;
KD = 18.14;
KE = 0.35;
KH = 1.2;
KS = 9.81;
KT = 0.35;
KV = 0.486;
KY = 29.94;
L  = 0.16;
R  = 5.4;
RM = 0.124;
RW = 0.064;
VD = 3.0;
VT = 0.75;
KI = 1.0;            % will be swept later

% Simulation parameters
stepsize     = 0.002;
comminterval = 0.002;
EndTime      = 10;
i = 0;

% Initial state vector
x = [0; 0; 0; 0; 0; 0; 0; 1; -12*pi/180; 0];
xdot = zeros(length(x),1);

% ==========================================================
% INITIALISE ERROR INTEGRATOR
% ==========================================================
psi_ref = 55*pi/180;   % reference yaw angle
E_int = 0;             % error integral
E_store = [];

% ==========================================================
%                    MAIN SIMULATION
% ==========================================================

for time = 0:stepsize:EndTime

    VT = VT_of_t(time);

    % Store data
    if rem(time, comminterval)==0
        i = i + 1;
        tout(i) = time;
        xout(i,:) = x;
        xdout(i,:) = xdot;
        E_store(i) = E_int;       % store integrated error
    end

    psi_dot = x(8); 
    E_int = E_int + abs(psi_dot) * stepsize;

    u = psi_ref;   % proportional controller

    % MODEL DERIVATIVE
    xdot = rover_state_space(x, u);

    % INTEGRATION
    x = rk4int('rover_state_space', stepsize, x, u);

end

% ==========================================================
%                PLOT MAIN SIMULATION RESULTS
% ==========================================================

figure;
subplot(2,1,1)
plot(tout, xout(:,9)*180/pi, 'LineWidth', 1.5); hold on
yline(55, 'g--', 'LineWidth', 1.2);   % 55° reference
xlabel("Time [s]")
ylabel("\psi [deg]")
title("Yaw Angle Response")
legend('Yaw angle', 'Reference 55°', 'Location', 'best')
grid on

% ==========================================================
%     CONSTANT vs DYNAMIC VT — FULL STATE COMPARISON
%     (Yaw angle, Forward velocity, Sway velocity)
% ==========================================================


% ==========================================================
%     1) CONSTANT VT SIMULATION
% ==========================================================
VT = 0.75;                   % constant speed
E_int = 0;
x_const = [0;0;0;0;0;0;0;1;-12*pi/180;0];
xdot_const = zeros(length(x_const),1);
i_const = 0;

for time = 0:stepsize:EndTime
    
    if rem(time, comminterval)==0
        i_const = i_const + 1;
        tout_const(i_const) = time;
        psi_const(i_const)  = x_const(9);  % yaw angle
        v_const(i_const)    = x_const(7);  % sway velocity
        VT_const(i_const)   = 0.75;        % constant VT
    end

    psi_dot = x_const(8);
    E_int = E_int + abs(psi_dot)*stepsize;
    u = psi_ref;

    xdot_const = rover_state_space(x_const, u);
    x_const = rk4int('rover_state_space', stepsize, x_const, u);
end



% ==========================================================
%     2) DYNAMIC VT SIMULATION
% ==========================================================
E_int = 0;
x_dyn = [0;0;0;0;0;0;0;1;-12*pi/180;0];
xdot_dyn = zeros(length(x_dyn),1);
i_dyn = 0;

for time = 0:stepsize:EndTime

    VT = VT_of_t(time);    % update VT dynamically

    if rem(time, comminterval)==0
        i_dyn = i_dyn + 1;
        tout_dyn(i_dyn) = time;
        psi_dyn(i_dyn)  = x_dyn(9);   % yaw
        v_dyn(i_dyn)    = x_dyn(7);   % sway velocity
        VT_dyn(i_dyn)   = VT;         % store VT(t)
    end

    psi_dot = x_dyn(8);
    E_int = E_int + abs(psi_dot)*stepsize;
    u = psi_ref;

    xdot_dyn = rover_state_space(x_dyn, u);
    x_dyn = rk4int('rover_state_space', stepsize, x_dyn, u);
end

% ----------------------------------------------------------
% SUBPLOT 1 — YAW ANGLE RESPONSE
% ----------------------------------------------------------
subplot(3,1,1); hold on; grid on;

plot(tout_const, psi_const*180/pi, 'g', 'LineWidth', 1.6, ...
    'DisplayName', 'Yaw — constant V_T');
plot(tout_dyn, psi_dyn*180/pi, 'r', 'LineWidth', 1.6, ...
    'DisplayName', 'Yaw — dynamic V_T(t)');

yline(55, 'g--', 'LineWidth', 1.1, 'DisplayName', 'Reference 55°');

xlabel("Time [s]");
ylabel("\psi [deg]");
title("Yaw Angle: Constant vs Dynamic Forward Velocity");
legend('Location','best');

% ----------------------------------------------------------
% SUBPLOT 3 — SWAY VELOCITY v(t)
% ----------------------------------------------------------
subplot(3,1,2); hold on; grid on;

plot(tout_const, v_const, 'g', 'LineWidth', 1.6, ...
    'DisplayName', 'v(t) — constant V_T');
plot(tout_dyn, v_dyn, 'r', 'LineWidth', 1.6, ...
    'DisplayName', 'v(t) — dynamic V_T(t)');

xlabel("Time [s]");
ylabel("v(t) [m/s]");
title("Sway Velocity: Constant vs Dynamic Forward Velocity");
legend('Location','best');


% ----------------------------------------------------------
% SUBPLOT 2 — FORWARD VELOCITY V_T(t)
% ----------------------------------------------------------
subplot(3,1,3); hold on; grid on;

plot(tout_const, VT_const, 'g--', 'LineWidth', 1.4, ...
    'DisplayName', 'Constant V_T = 0.75');

plot(tout_dyn, VT_dyn, 'r', 'LineWidth', 1.6, ...
    'DisplayName', 'Dynamic V_T(t)');

% ------------------------------------------
% Add original data points
% ------------------------------------------
x_nodes  = [0  1.2  3.2  6  9  10];
VT_nodes = [0.72 0.8 1.5 0.6 0.4 0.2];

plot(x_nodes, VT_nodes, 'ko', 'MarkerSize', 7, ...
     'MarkerFaceColor','y', 'DisplayName','Data Points');

xlabel("Time [s]");
ylabel("V_T(t) [m/s]");
title("Forward Velocity Profiles: Constant vs Dynamic");
legend('Location','best');



% ==========================================================
%            KI SWEEP — MULTIPLE YAW CURVES
% ==========================================================

KI_values = [0 0.5 0.75 1 1.25 1.5];   % try different KI
colors = lines(length(KI_values));

figure; hold on; grid on
title('Yaw Angle \psi(t) for Different KI Gains')
xlabel('Time [s]')
ylabel('\psi [deg]')

yline(55, 'g--', 'LineWidth', 1.3, 'DisplayName', 'Reference 55°');

for k = 1:length(KI_values)

    KI = KI_values(k);     % <---- CHANGE: KI varied, Gc fixed
    E_int = 0;

    x = [0; 0; 0; 0; 0; 0; 0; 1; -12*pi/180; 0];
    xdot = zeros(length(x),1);

    ii = 0;
    tout_KI = [];
    psi_KI  = [];

    % -------------------------------
    %  Run simulation for this KI
    % -------------------------------
    for time = 0:stepsize:EndTime

        if rem(time, comminterval)==0
            ii = ii + 1;
            tout_KI(ii) = time;
            psi_KI(ii)  = x(9);
        end

        psi_dot = x(8);   % yaw rate
        E_int = E_int + abs(psi_dot) * stepsize;

        u = psi_ref;

        xdot = rover_state_space(x, u);
        x = rk4int('rover_state_space', stepsize, x, u);

    end

    % Save total |error| integral for this KI
    total_error(k) = E_int;

    % Plot yaw curve
    plot(tout_KI, psi_KI*180/pi, ...
        'Color', colors(k,:), 'LineWidth', 1.5, ...
        'DisplayName', sprintf('KI = %.2f', KI));

end

legend show

% ==========================================================
%            PRINT TABLE OF TOTAL ERRORS
% ==========================================================

fprintf("\n==============================================\n");
fprintf("      KI VALUE     |   TOTAL ABS ERROR (rad·s)\n");
fprintf("==============================================\n");

for k = 1:length(KI_values)
    fprintf("    %6.2f        |     %10.5f\n", KI_values(k), total_error(k));
end

fprintf("==============================================\n\n");
