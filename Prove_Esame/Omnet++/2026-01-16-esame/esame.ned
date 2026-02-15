import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Sink;
import org.omnetpp.queueing.Delay;
import org.omnetpp.queueing.Clone;

network esame {

    parameters:
        
        double lambda = default(40);
        double mu_1 = default(25);
        double mu_2 = default(40);

        srv_1.serviceTime = 1s * exponential(1 / mu_1);
        srv_2.serviceTime = 1s * exponential(1 / mu_2);


        src.interArrivalTime = 1s * exponential(1 / lambda);
        r.randomGateIndex=default(uniform(0,1.0)<=0.3125?0:1);


        //src[*].interArrivalTime = exponential(1s/lambda);
        //srv.serviceTime = 1s * exponential(1 / mu);
        //r.routingAlgorithm="random";
        

    submodules:
		src: Source;
        srv_1: Queue;
        srv_2: Queue;
        c_1: Clone;
        c_2: Clone;
        r: Router;
        sink_1: Sink;
        sink_2: Sink;
        sink_g: Sink;

    connections:
        src.out --> r.in++;
        
        r.out++ --> srv_1.in++;
        r.out++ --> srv_2.in++;

        srv_1.out --> c_1.in++;
        srv_2.out --> c_2.in++;

        c_1.out++ --> sink_1.in++;
        c_1.out++ --> sink_g.in++;

        c_2.out++ --> sink_2.in++;
        c_2.out++ --> sink_g.in++;

        //MAPPA di Ingressi/Uscite
        //source -> out; 
        //queue -> in[]; out;
        //router -> in[]; out[];
        //sink -> in[];
        //delay -> in[], out;

}