# Router
Questo modulo si occupa dell'invio dei messaggi ai suoi output seguendo l'algoritmo specificato.
```ned
simple Router
{
    parameters:
        @group(Queueing);
        @display("i=block/routing");
        string routingAlgorithm @enum("random","roundRobin","shortestQueue","minDelay") = default("random");
        volatile int randomGateIndex = default(intuniform(0, sizeof(out)-1));    // the destination gate in case of random routing
    gates:
        input in[];
        output out[];
}
```
In particolare se uso componente router, nel file `.ned` posso specificare la politica di routing ed eventualmente `randomGateIndex` (come si sceglie il gate se la policy è random"):
```ned
import org.omnetpp.queueing.Router;

network MM1 {
    parameters:
        r.routingAlgorithm="random"
        r.randomGateIndex=(uniform(0,10.0)<=6.0?0:1)

    connections:
        # router ha un array vuoto di porte di input, input[]
        # router ha un array vuoto di porte di output, output[]
}
```