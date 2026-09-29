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

clear all

% Define and initialise the model input and any model parameters
% as global variables so that they can be read in the function model.m.

global mu 

mu = 1;

% Define parameters for the simulation

stepsize = 0.001;				% Integration step size
comminterval = 0.001;			% Communications interval
EndTime = 40;					% Duration of the simulation (final time)
i = 0;							% Initialise counter for data storage

% Initial conditions of all states and state derivatives

u = 0;
x = [0.5,-0.5, 0.5]';
xdot = [0,0,0]';

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
    
    u = -(24*x(1) + 18.64*x(2));

    % DERIVATIVE SECTION
	%
	% The DERIVATIVE SECTION contains the statements needed to evaluate the
	% state derivatives - these statements define the dynamic model (model.m)
	
	xdot = chaotic(x,u);

	% END OF DERIVATIVE SECTION
	%
	% INTEG SECTION
	% 
    % Numerical integration of the state derivatives for this time interval
   
    x = rk4int('chaotic', stepsize, x, u);    
   
    % END OF INTEG SECTION
   
end

% END OF DYNAMIC SEGMENT
%
% TERMINAL SEGMENT
%
% The TERMINAL SEGMENT contains statements that are executed after the simulation 
% is complete e.g. plotting results

figure(8)										% define figure window number
clf												% clear figure
plot(tout,xout(:,1),'bo-')
xlabel('time [s]')
ylabel('states')
title("CHAOTIC OH YEAH BABYYYY")
hold on
grid on
plot(tout,xout(:,2),'ro-')
plot(tout,xout(:,3),'go-')
hold off

% END OF TERMINAL SECTION
%
% END OF SIMULATION PROGRAM

