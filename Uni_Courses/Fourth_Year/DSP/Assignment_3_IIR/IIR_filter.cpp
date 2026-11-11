// ========= Direct Form I ===========

class DirectFormI {

    // Filter coefficients
    double b[3];
    double a[3];
    double Q_scaling;

    // Four delay buffers
    double input_delay_1;
    double input_delay_2;
    double output_delay_1;
    double output_delay_2;

    // Accumulator
    double accumulator;

} ;

// ========= Direct Form II ===========

class DirectFormII { 

    // Filter coefficients
    double b[3];
    double a[3];

    // Two delay buffers
    double delay_1;
    double delay_2;

    // Two accumulators
    double input_accumulator;
    double output_accumulator;

};