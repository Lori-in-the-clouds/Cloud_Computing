[General]
ned-path = .;../queueinglib
network = esame
repeat = 5
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false

[Config Fase1]
**.sink.lifeTime.result-recording-modes = +mean
**.label="fase1"
**.N = 20

%for n in [15, 20, 25, 30, 35, 40, 45, 50]:
[Config Fase2_${n}]
**.N = ${n}
**.sink.lifeTime.result-recording-modes = +mean
**.label="fase2"
%endfor