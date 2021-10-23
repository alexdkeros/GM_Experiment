Scaling Geometric Monitoring over Distributed Streams
=====================================================

Implemetation for my undergraduate thesis at the Technical University of Crete, under the supervision of Dr. Samoladas.
The submitted thesis can be found [here](https://dias.library.tuc.gr/view/65984).
The latex files are [here](https://github.com/alexdkeros/GM_Thesis_latex).
Abstract
--------

Modern applications, such as telecommunication and sensor networks, have brought distributeddata streams to the foreground, 
with monitoring tasks being an important aspect of such systems. The inefficiency of collecting data to a central point for processing 
dictates the need to devise localor semi-local algorithms that aim to reduce the communication overhead while retaining accuracystandards. 
The geometric monitoring method [Sharfman et al., “A Geometric Approach to MonitoringThreshold Functions over Distributed Data Streams”, ACM SIGMOD ’06 ICMD] 
provides a frame-work for enforcing local constraints at distributed nodes, as well as a method for resolving violationsnot representing the system’s state i.e., 
false alarms, in order to reduce the necessary communi-cation with the coordinating node. Furthermore, successive work proposed optimizations to the selection 
process of the nodes participating to the set that resolves such violations.We propose a heuristic method that exploits data stream characteristics and utilizes 
multi-objective optimization in order to avert, or delay, successive false alarms by optimally positioningvector representations of data streams during the 
violation resolution process. Additionally, ahierarchical node clustering method for deterministic and optimal node selection, found in 
[ Kerenet al., “Geometric Monitoring of Heterogeneous Streams”, IEEE Trans. Knowl. Data Eng., 2014], isimproved and simplified. 
Extensive experimentation on real-world and synthetic datasets showcasethat the proposed methods can reduce the communication burden in half, 
compared to that of theoriginal geometric monitoring method. 
