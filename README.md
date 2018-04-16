# Unmanned-Aerial-Vehicle-Tracking
As Unmanned Aerial Vehicle’s (UAV) battery life and stability develop, 
multiple UAVs are having more and more applications in the uninterrupted 
patrol and security. Thus UAV’s searching, tracking and trajectory planning 
become important issues. This paper proposes an online distributed algorithm 
used in UAV’s tracking and search- ing, with the consideration of UAV’s 
practical need to recharge under limited power. We propose a Quantum 
Probability Model to describe the partially observable target positions, 
and we use Upper Confidence Tree (UCT) algorithm to find out the best 
searching and tracking route based on this model. We also introduce the 
Teammate Learning Model to handle the nonstationary problems in distributed 
reinforcement learning.

## Problem and Algorithm
The explanation of the problem and the algorithm can be found [here](http://ieeexplore.ieee.org/document/7868620/).

## Requirements
* Python 2.7

## Experiments
To run the experiments, first set up the parameters of the algorithm and testing environment in ``test_file.py``:
* ``all_work``: a dict containing a batch of experiment parameters.
* ``name``: The name of this experiment. The experiment record will be saved
in ``name``.txt.
* ``T``: Number of search times in each UCT planing, as explained in the paper.
* ``D``: The depth of the search tree, aas explained in the paper.
* ``test_time``: Repeat this experiment ``test_time`` times.
* ``size``: The size of the search area.
* ``base_lists``: A list of the locations of the charging bases. You can set
any number of charging bases in the experiment.
* ``plan_lists``: A list of the initial positions of the drones. You can set
any number of drones in the experiment.

Then you can start the experiment using command:

```
python test_file.py
```

The simulation of each step will be printed to ``stdout``.
The log of each experiment will be stored in the corresponding
``name``.txt. 