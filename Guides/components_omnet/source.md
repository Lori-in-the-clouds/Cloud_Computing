# Source
Questo modulo si occupa della generazione di jobs. Si può specificare il numero, l'orario di inizio e di fine e l'intervallo tra la generazione dei job. La generazione dei job termina quando si produce il numero di job impostati o quando si raggiunge il limite di tempo.
```ned
package org.omnetpp.queueing;

//
// A module that generates jobs. One can specify the number of jobs to be generated,
// the starting and ending time, and interval between generating jobs.
// Job generation stops when the number of jobs or the end time has been reached,
// whichever occurs first. The name, type and priority of jobs can be set as well.
//
simple Source
{
    parameters:
        @group(Queueing);
        @signal[created](type="long");
        @statistic[created](title="the number of jobs created";record=last;interpolationmode=none);
        @display("i=block/source");
        int numJobs = default(-1);               // number of jobs to be generated (-1 means no limit)
        volatile double interArrivalTime @unit(s); // time between generated jobs
        string jobName = default("job");         // the base name of the generated job (will be the module name if left empty)
        volatile int jobType = default(0);       // the type attribute of the created job (used by classifers and other modules)
        volatile int jobPriority = default(0);   // priority of the job
        double startTime @unit(s) = default(interArrivalTime); // when the module sends out the first job
        double stopTime @unit(s) = default(-1s); // when the module stops the job generation (-1 means no limit)
    gates:
        output out;
}
```
In particolare se uso componente Source, nel file `.ned` specifico `lambda` e `interarrival time`:
```ned
import org.omnetpp.queueing.Source;

network MM1 {
    parameters:
        ...
        double lambda = mu * rho;
        src.interArrivalTime = 1s * exponential(1 / lambda);
        

    connections:
        # source ha una sola porta di output out
}
```
