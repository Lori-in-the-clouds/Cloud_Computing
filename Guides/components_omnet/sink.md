# Sink
Rappresenta il punto finale del flusso: distrugge o archivia i pacchetti in arrivo, aggregando i dati necessari per l'analisi delle statistiche prestazionali.
```ned
simple Sink
{
    parameters:
        @group(Queueing);
        @display("i=block/sink");
        @signal[lifeTime](type="simtime_t");
        @signal[totalQueueingTime](type="simtime_t");
        @signal[totalDelayTime](type="simtime_t");
        @signal[totalServiceTime](type="simtime_t");
        @signal[queuesVisited](type="long");
        @signal[delaysVisited](type="long");
        @signal[generation](type="long");
        @statistic[lifeTime](title="lifetime of arrived jobs";unit=s;record=vector,mean,max;interpolationmode=none);
        @statistic[totalQueueingTime](title="the total time spent in queues by arrived jobs";unit=s;record=vector?,mean,max;interpolationmode=none);
        @statistic[totalDelayTime](title="the total time spent in delay nodes by arrived jobs";unit=s;record=vector?,mean,max;interpolationmode=none);
        @statistic[totalServiceTime](title="the total time spent  by arrived jobs";unit=s;record=vector?,mean,max;interpolationmode=none);
        @statistic[queuesVisited](title="the total number of queues visited by arrived jobs";record=vector?,mean,max;interpolationmode=none);
        @statistic[delaysVisited](title="the total number of delays visited by arrived jobs";record=vector?,mean,max;interpolationmode=none);
        @statistic[generation](title="the generation of the arrived jobs";record=vector?,mean,max;interpolationmode=none);
        bool keepJobs = default(false); // whether to keep the received jobs till the end of simulation
    gates:
        input in[];
}
```
In particolare se uso componente sink non devo configurare nulla, poi configurero' statistiche nel file `.ini`.
```ned
import org.omnetpp.queueing.Sink;

network MM1 {
    parameters:
        ...

    connections:
        # sink ha un array vuoto di porte di input, input[]
        # sink non ha porte di output
}

```