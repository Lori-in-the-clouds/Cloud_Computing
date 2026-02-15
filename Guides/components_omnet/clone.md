# Clone
Utilizzato per la duplicazione dei messaggi (job) all'interno della rete.
```ned
package org.omnetpp.queueing;

//
// Sends out incoming messages on ALL output gates. The original
// message is sent out on out[0]. The other output gates will get a copy
// of the original message.
//
simple Clone
{
    parameters:
        @group(Queueing);
        @display("i=block/fork");
        bool changeMsgNames = default(true);  // whether to change the message names when they go through the module
    gates:
        input in[];
        output out[];
}
```
Visibile anche con il comando seguente eseguito dalla cartella di installazione di omnet:
```bash
cat samples/queueinglib Clone.ned
```



