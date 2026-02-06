[General]
ned-path = .;../queueinglib
network = esame
repeat = 10
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false

[Config CONF_1_mu_1]
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_1)
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_1)
**.srv[*].recording.lifeTime.result-recording-modes = +mean
**.srv[*].recording.busyTime.result-recording-modes = +timeavg
**.label = "fase_1_mu1"
**.N = 45

[Config CONF_1_mu_2]
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_2)
**.srv[*].recording.lifeTime.result-recording-modes = +mean
**.srv[*].recording.busyTime.result-recording-modes = +timeavg
**.label = "fase_1_mu2"
**.N = 45

%for i in [30, 35, 40, 45, 50, 55]:
[Config CONF_2_mu_1_${int(i)}]
**.N = ${i}
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_1)
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_1)
**.srv[*].recording.lifeTime.result-recording-modes = +mean
**.srv[*].recording.busyTime.result-recording-modes = +timeavg
**.label = "fase_2_mu1"
%endfor


%for j in [15, 20, 25, 35, 45, 55]:
[Config CONF_2_mu_2_${int(j)}]
**.N = ${j}
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_2)
**.srv[*].serviceTime = 1s * exponential(1 / parent.mu_2)
**.srv[*].recording.lifeTime.result-recording-modes = +mean
**.srv[*].recording.busyTime.result-recording-modes = +timeavg
**.label = "fase_2_mu2"
%endfor
