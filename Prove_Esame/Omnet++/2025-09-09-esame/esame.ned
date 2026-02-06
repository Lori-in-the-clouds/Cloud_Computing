import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Sink;

network esame
{
	parameters:
        int N = default(44);
        int lambda = default(200); 
        double mu_1 = default(8);
        double mu_2 = default(16);
		src.interArrivalTime = exponential(1s/lambda);
        r.routingAlgorithm="random";

	submodules:
		src: Source;
        r: Router;
        srv[N]: Queue;
        sink: Sink;
        
	connections:
        src.out --> r.in++;
	    for i=0..N-1 { 
		    r.out++ --> srv[i].in++;
            srv[i].out --> sink.in++;
	    }
}