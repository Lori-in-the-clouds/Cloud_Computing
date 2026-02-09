[General]
ned-path = .;../queueinglib
network = esame
repeat = 5
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false


[Config Fase_1_mu_1]
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_1)
**.sink.lifeTime.result-recording-modes = +mean
**.label="F1_mu1"

[Config Fase_1_mu_2]
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_2)
**.sink.lifeTime.result-recording-modes = +mean
**.label="F1_mu2"
**.N = 40


%for i in [25, 30, 35, 40, 45, 50]:
[Config Fase_2_${i}_mu1]
**.N = ${i}
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_1)
**.sink.lifeTime.result-recording-modes = +mean
**.label="F2_mu1"
%endfor


%for j in [15, 20, 25, 30, 35, 40, 45, 50]:
[Config Fase_2_${j}_mu2]
**.N = ${j}
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_2)
**.sink.lifeTime.result-recording-modes = +mean
**.label="F2_mu2"
%endfor
