import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Sink;
import org.omnetpp.queueing.Delay;


network esame {

    parameters:

        double f_l = default (0.7);
        double lambda = default(10);
        
        double lambda_l = lambda * f_l;
        double lambda_c = lambda * (1 - f_l);

        double mu_l = 10;
        double mu_c = 1 / (0.070);

        src_l.interArrivalTime = 1s * exponential(1 / lambda_l);
        src_c.interArrivalTime = 1s * exponential(1 / lambda_c);

        srv_l.serviceTime = 1s * exponential(1 / mu_l);
        srv_c.serviceTime = 1s * exponential(1 / mu_c);

        delay.delay = 1s * exponential(1 / mu_l);

    submodules:
		src_l: Source;
        src_c: Source;
        
        delay: Delay;

        srv_l: Queue;
        srv_c: Queue;

        sink: Sink;

    connections:

        src_l.out --> srv_l.in++;
        srv_l.out --> sink.in++;

        src_c.out --> srv_c.in++;
        srv_c.out --> delay.in++;
        delay.out --> sink.in++;
    

}