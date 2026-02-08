# Classifier
A differenza di un Router che può seguire logiche random o round-robin, il Classifier agisce come un demultiplexatore intelligente. Esso ispeziona ogni job in transito e lo indirizza a una specifica porta del vettore di uscita `out[]`.
```ned
simple Classifier
{
    parameters:
        @group(Queueing);
        @display("i=block/classifier");
        string dispatchField @enum("type","priority") = default("type");
    gates:
        input in[];
        output out[];
        output rest;     // messages that were not classified, RICORDATI DI INSERIRE ANCHE QUESTO
}
```
Visibile anche con il comando seguente eseguito dalla cartella di installazione di omnet:
```bash
cat samples/queueinglib Classifier.ned
```
## Parametro DispatcherField
Questo parametro rappresenta il criterio di selezione del modulo. Può assumere principalmente due valori:
- `"type"`: il modulo legge la proprietà jobType del pacchetto. Se jobType è un intero `n`, il pacchetto verrà inviato all'uscita `out[n]`.
- `"priority"`: il modulo legge il campo priority del pacchetto per decidere l'instradamento.
---