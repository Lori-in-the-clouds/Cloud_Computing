[General]
ned-path = .;../queueinglib
network = esame
repeat = 5
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false

[Config Fase_1]
**.sink_1.lifeTime.result-recording-modes = +mean
**.sink_2.lifeTime.result-recording-modes = +mean
**.sink_g.lifeTime.result-recording-modes = +mean
**.p = 0
**.label="F1"

%for p in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
[Config Fase_2_p_${"%03d" % int(p * 100)}]
**.p = ${p}
**.r.randomGateIndex=(uniform(0,1.0)<=${p}?0:1)
**.sink_1.lifeTime.result-recording-modes = +mean
**.sink_2.lifeTime.result-recording-modes = +mean
**.sink_g.lifeTime.result-recording-modes = +mean
**.label="F2"
%endfor