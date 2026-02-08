import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Sink;
import org.omnetpp.queueing.Delay;
import org.omnetpp.queueing.Classifier;


network esame {

    parameters:
        double lambda = default(6);
        double mu = default(10);

    submodules:
		src_low: Source;
        src_high: Source;

        srv_low: Queue;
        srv_high: Queue;

        classifier: Classifier;
       
        sink_low: Sink;
        sink_high: Sink;

    connections:
        src_low.out --> srv_low.in++;
        srv_low.out --> classifier.in++;

        src_high.out --> srv_high.in++;
        srv_high.out --> classifier.in++;

        classifier.out++ --> sink_low.in++;
        classifier.out++ --> sink_high.in++;
        classifier.rest --> sink_low.in++;
        
        //MAPPA di Ingressi/Uscite
        //source -> out; 
        //queue -> in[]; out;
        //router -> in[]; out[];
        //sink -> in[];
        //delay -> in[], out;

}