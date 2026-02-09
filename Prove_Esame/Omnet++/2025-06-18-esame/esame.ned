import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Sink;
import org.omnetpp.queueing.Delay;

network esame {

    parameters:
        int N = default(40);
        double mu_1 = default(10);
        double mu_2 = default(15);
        double lambda = 200;

        src.interArrivalTime = 1s * exponential(1 / lambda);
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

        //MAPPA di Ingressi/Uscite
        //source -> out; 
        //queue -> in[]; out;
        //router -> in[]; out[];
        //sink -> in[];
        //delay -> in[], out;

}