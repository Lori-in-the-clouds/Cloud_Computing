# Queue
Questo modulo rappresenta una coda con un server build-in (@statistic[busy]).
```ned
simple Queue
{
    parameters:
        @group(Queueing);
        @display("i=block/activeq;q=queue");
        @signal[dropped](type="long");
        @signal[queueLength](type="long");
        @signal[queueingTime](type="simtime_t");
        @signal[busy](type="bool");
        @statistic[dropped](title="drop event";record=vector?,count;interpolationmode=none);
        @statistic[queueLength](title="queue length";record=vector,timeavg,max;interpolationmode=sample-hold);
        @statistic[queueingTime](title="queueing time at dequeue";record=vector?,mean,max;unit=s;interpolationmode=none);
        @statistic[busy](title="server busy state";record=vector?,timeavg;interpolationmode=sample-hold);

        int capacity = default(-1);    // negative capacity means unlimited queue
        bool fifo = default(true);     // whether the module works as a queue (fifo=true) or a stack (fifo=false)
        volatile double serviceTime @unit(s);
    gates:
        input in[];
        output out;
}
```
In particolare se uso componente Queue, nel file `.ned` specifico la capacità/lunghezza della queue e il `service time`:
```ned
import org.omnetpp.queueing.Queue;

network MM1 {
    parameters:
        ...
        srv.capacity = K;

        # Se service time M
        srv.serviceTime = 1s * exponential(1 / mu);
        
        # Se service time G
        # double cv=default(1.0); //coefficiente di variazione (apertura della gaussiana)
        # srv[*].serviceTime = 1.0s*lognormal(log(1.0/(mu*sqrt(1+cv^2))), sqrt(log(1+cv^2)));

    connections:
        # queue ha una array vuoto di porte di input, input[]
        # queue ha una sola porta di output out
}
```