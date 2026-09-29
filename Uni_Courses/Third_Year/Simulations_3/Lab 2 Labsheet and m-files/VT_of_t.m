function VT = VT_of_t(x)
% VT_OF_T - Newton interpolating polynomial for Rover Forward Velocity
%
%   VT(x) = 0.72
%           + 0.0667*x
%           + 0.0885*x*(x - 1.2)
%           - 0.0381*x*(x - 1.2)*(x - 3.2)
%           + 0.0068*x*(x - 1.2)*(x - 3.2)*(x - 6)
%           - 0.0011*x*(x - 1.2)*(x - 3.2)*(x - 6)*(x - 9)
%
%   Input:
%       x  - time (scalar or vector)
%
%   Output:
%       VT - forward velocity at time x (m/s)

VT = 0.72 ...
    + 0.0667 .* x ...
    + 0.0885 .* x .* (x - 1.2) ...
    - 0.0381 .* x .* (x - 1.2) .* (x - 3.2) ...
    + 0.0068 .* x .* (x - 1.2) .* (x - 3.2) .* (x - 6) ...
    - 0.0011 .* x .* (x - 1.2) .* (x - 3.2) .* (x - 6) .* (x - 9);
end
