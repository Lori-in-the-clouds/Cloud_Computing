[General]
ned-path = .;../queueinglib
network = esame
repeat = 5
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false


[Config CONF_1]
**.sink[*].lifeTime.result-recording-modes = +mean
**.label = "Fase1"


%for f in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.88, 0.9]:
[Config CONF_2_${"%03d" % int(f * 100)}]
**.f_l = ${f}
**.sink[*].lifeTime.result-recording-modes = +mean
**.label = "Fase2"
%endfor

