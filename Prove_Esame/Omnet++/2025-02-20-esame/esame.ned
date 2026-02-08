import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Sink;
import org.omnetpp.queueing.Delay;

network esame {

    parameters:
        double lambda = default(100);
        int N = default(44);
        double mu = default(10);
        double cv = default(3);
        
        src.interArrivalTime = 1s * exponential(1 / lambda);
        srv[*].serviceTime = 1s * lognormal(log(1.0 / (mu * sqrt(1 + cv^2))), sqrt(log(1 + cv^2)));
        r.routingAlgorithm="random";
        
    submodules:
		src: Source;
        srv[N]: Queue;
        sink: Sink;
        r: Router;

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