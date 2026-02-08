[General]
ned-path = .;../queueinglib
network = esame
repeat = 5
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false


%for i in [0,1,2,3]:
[Config Fase_1_${i}]
**.srv_low.serviceTime = 1s * exponential(1 / parent.mu)
**.srv_high.serviceTime = 1s * exponential(1 / parent.mu)
**.src_low.interArrivalTime = 1s * exponential(1 / (parent.lambda - ${i}))
**.src_high.interArrivalTime = 1s * exponential(1 / (parent.lambda + ${i}))
**.sink_low.lifeTime.result-recording-modes = +mean, +max
**.sink_high.lifeTime.result-recording-modes = +mean, +max
**.srv_low.busy.result-recording-modes = +timeavg
**.srv_high.busy.result-recording-modes = +timeavg
**.label="fase_1"
**.sigma = ${i}

**.src_low.jobType = 0
**.src_high.jobType = 1
**.classifier.dispatchField = "type"
%endfor

%for i in [0,1,2,3]:
[Config Fase_2_${i}]
**.srv_low.serviceTime = 1s * exponential(1 / (parent.mu + ${i}))
**.srv_high.serviceTime = 1s * exponential(1 / (parent.mu - ${i}))
**.src_low.interArrivalTime = 1s * exponential(1 / parent.lambda)
**.src_high.interArrivalTime = 1s * exponential(1 / parent.lambda)
**.srv_low.busy.result-recording-modes = +timeavg
**.srv_high.busy.result-recording-modes = +timeavg
**.sink_low.lifeTime.result-recording-modes = +mean, +max
**.sink_high.lifeTime.result-recording-modes = +mean, +max
**.label="fase_2"
**.sigma = ${i}

**.src_low.jobType = 0
**.src_high.jobType = 1
**.classifier.dispatchField = "type"
%endfor