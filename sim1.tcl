#Es crea l'objecte simulador
# TCP Original (RFC 793)
if {$argc == 4} {
    set karn   [lindex $argv 0] 
    set jacobson       [lindex $argv 1] 
    set AD          [lindex $argv 2]
    set SlowStart    [lindex $argv 3]

} else {
    puts "      CBR0-UDP n0"
    puts "                \\"
    puts "                 n2 ---- n3"
    puts "                /"
    puts "      CBR1-TCP n1 "
    puts ""
    puts "  Usage: ns $argv0 karn (true|false) jacobson (true|false) AD (true|false) SlowStart (true|false)"
    puts ""
    exit 1
}


set ns [new Simulator]


#S'obre l'arxiu per traçar resultats
#
if {$karn==false && $jacobson==false && $AD==false && $SlowStart==false} {
   set arxiu "original"
} elseif {$karn==true && $jacobson==false && $AD==false && $SlowStart==false} {
   set arxiu "karn" 
} elseif {$karn==false && $jacobson==true && $AD==false && $SlowStart==false} {
   set arxiu "jacobson" 
} elseif {$karn==false && $jacobson==true  && $AD==true && $SlowStart==false} {
    set arxiu "additive"
} elseif {$karn==false && $jacobson==true  && $AD==false && $SlowStart==true} {
    set arxiu "slow"
} else {
    set arxiu "ERROR"
}

set nf [open $arxiu.tr w]
$ns trace-all $nf
set nff [open $arxiu.rtt w]

#Definim el procediment per acabar
proc finish {} {
        global ns nf nff
        
        # pot donar problemes
        $ns flush-trace
        close $nf
        close $nff
        exit 0
}

# Procediment per gravar els temps del TCP
proc grava { } {
	global ns tcp0 nff
    set rtt  [expr [$tcp0 set rtt_]  * [$tcp0 set tcpTick_]]
    set srtt  [expr ([$tcp0 set srtt_] >> [$tcp0 set T_SRTT_BITS]) * [$tcp0 set tcpTick_]]
    set rttvar  [expr ([$tcp0 set rttvar_] >> [$tcp0 set T_RTTVAR_BITS]) * [$tcp0 set tcpTick_]]
    set bo [expr [$tcp0 set backoff_]]  
    set cw  [expr [$tcp0 set cwnd_] * [$tcp0 set tcpTick_]]
#  bo = 1, 2, 4, ...
    set rto [expr [$tcp0 set rto_] * [$tcp0 set tcpTick_]]
	set now [$ns now]
	puts $nff "$now $rtt $srtt $rto [expr 0.5*($bo-1)] $cw"

	$ns at [expr $now+0.1] "grava"

}

#Creem 4 nodes
#
#  n0
#  \
#   \
#    n2--------n3
#   /
#  /
# n1
 
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]



#Creem línies duplex entre els nodes
$ns duplex-link $n0 $n2 5Mb 20ms DropTail
$ns duplex-link $n1 $n2 5Mb 20ms DropTail
$ns duplex-link $n2 $n3 1Mb 50ms DropTail


# Pel node 0; un agent UDP amb trànsit CBR
set udp0 [new Agent/UDP]
$ns attach-agent $n0 $udp0
set cbr0 [new Application/Traffic/CBR]
$cbr0 set rate_ 0.5Mbps
$cbr0 attach-agent $udp0
$udp0 set class_ 0



# Pel node 1:  Agent TCP que empra l'algorisme Karn/Partridge. Modifiquem el temporitzador tcpTick 
# Amb generador de trànsit CBR
set tcp0 [new Agent/TCP/RFC793edu]
$tcp0 set class_ 1
$tcp0 set add793karnrtt_ $karn
$tcp0 set add793jacobsonrtt_ $jacobson
# pone a doble el T.O.
$tcp0 set add793expbackoff_ true
$tcp0 set add793slowstart_ $SlowStart
$tcp0 set add793additiveinc_ $AD
# additivi noseqe 
$ns attach-agent $n1 $tcp0
$tcp0 set tcpTick_ 0.01
$tcp0 set window_ 40

set cbr1 [new Application/Traffic/CBR]
$cbr1 set rate_ 0.5Mbps
$cbr1 attach-agent $tcp0

# Pel node 3: 2 Sinks
set null0 [new Agent/Null]
$ns attach-agent $n3 $null0
set null1 [new Agent/TCPSink]
$ns attach-agent $n3 $null1

# Connectem els agents
$ns connect $udp0 $null0  
$ns connect $tcp0 $null1

# A 5s arranquem la font CBR0. Als 10s. l'aturem

$ns at 5.0 "$cbr0 start"
$ns at 10.0 "$cbr0 stop"

$ns at 0.0 "$cbr1 start"
$ns at 0.0 "grava"
$ns at 15.0 "finish"

$tcp0 attach-trace $nff

#Executem la simulació
$ns run
