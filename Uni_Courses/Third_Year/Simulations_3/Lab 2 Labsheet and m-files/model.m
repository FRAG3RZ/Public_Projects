% This function represents the dynamic equations for Van der Pol's oscillator 
%
% This is the DERIVATIVE SECTION of the simulation.
%
% The current time, state and input values are passed to the function as arguments
% and the function returns the state derivative.
function xdot = model(x,u)

global mu					% global parameter transferred from main program

xdot(1,1) = x(2);
xdot(2,1) = -mu*(x(1)*x(1) - 1)*x(2)-x(1);
