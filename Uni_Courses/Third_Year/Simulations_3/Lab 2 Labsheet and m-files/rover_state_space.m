function xdot = rover_state_space(x,u)
% ==============================================================
% Rover Turning Control System — Continuous State-Space Model
% ==============================================================
% This function implements the 9-state dynamic model described in
% the Simulation of Engineering Systems 3 assignment (Part 1).
%
% States (x):
%   x(1) = iL   → left motor current (A)
%   x(2) = iR   → right motor current (A)
%   x(3) = wML  → left motor angular speed (rad/s)
%   x(4) = wMR  → right motor angular speed (rad/s)
%   x(5) = wWL  → left wheel angular speed (rad/s)
%   x(6) = wWR  → right wheel angular speed (rad/s)
%   x(7) = v    → sway velocity (m/s)
%   x(8) = r    → yaw rate (rad/s)
%   x(9) = psi  → yaw angle (rad)
%
% Input (u):
%   u = reference heading ψ_ref (radians)
%
% Output:
%   xdot = time derivative of state vector [9×1]
% ==============================================================

global BS Gc JM JW KC KD KE KH KS KT KV KY L R RM RW VD VT KI 

% --- unpack current states from x input ---
iL  = x(1);   iR  = x(2);
wML = x(3);   wMR = x(4);
wWL = x(5);   wWR = x(6);
v   = x(7);   r   = x(8);   
psi = x(9);   integral_error  = x(10);

% Proportional control element
d_psi = (KC*u - KH*psi);

% --- NEW TURNING CONTROL---
dV = Gc * (d_psi + KI * integral_error); 

% Intergral error for the next iteration is the current delta Psi
d_integral_error = d_psi;

% --- Motor electrical dynamics (eq. 2) ---
diL = (1/L) * (VD + dV - R*iL - KE*wML);
diR = (1/L) * (VD - dV - R*iR - KE*wMR);

% --- Motor mechanical dynamics (eq. 3) ---
dwML = (1/JM) * (KT*iL - BS*(wML - wWL));
dwMR = (1/JM) * (KT*iR - BS*(wMR - wWR));

% --- Wheel mechanical dynamics (eq. 4) ---
dwWL = (1/JW) * (BS*(wML - wWL));
dwWR = (1/JW) * (BS*(wMR - wWR));

% --- Wheel forces (eqs. 5–6) ---
FL = 2*KT*iL / RW;    % total left-side force [N]
FR = 2*KT*iR / RW;    % total right-side force [N]

% --- Rover body sway & yaw dynamics (eqs. 7–8) ---
dv = -KS*v + VT*r + KV*(FL + FR)*v / VT;
dr = -VT*r + KD*v + KY*(FL - FR)*RM;
dpsi = r;             % kinematic relationship ψ̇ = r

% --- assemble derivative vector ---
xdot = [diL; diR; dwML; dwMR; dwWL; dwWR; dv; dr; dpsi; d_integral_error];

end
