# Delay
Ritarda il transito dei messaggi in base a un valore fisso o a una distribuzione statistica. Poiché i tempi di elaborazione possono variare per ogni pacchetto, l'ordine di uscita dei messaggi **non è necessariamente identico** a quello di ingresso.
```ned
simple Delay
{
    parameters:
        @group(Queueing);
        @signal[delayedJobs](type="long");
        @statistic[delayedJobs](title="number of delayed jobs";record=vector?,timeavg,max;interpolationmode=sample-hold);
        @display("i=block/delay");
        volatile double delay @unit(s); // the requested delay time (can be a distribution)
    gates:
        input in[];                     // the incoming message gates
        output out;                     // outgoing message gate
}
```
Visibile anche con il comando seguente eseguito dalla cartella di installazione di omnet:
```bash
cat samples/queueinglib Delay.ned
```