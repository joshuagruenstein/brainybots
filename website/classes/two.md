# Decisions, Decisions, Decisions

Today's class builds upon the probability fundamentals from class one, and introduces methods of *decision making* using inferred probabilities.

## Lab \#2: trapped in the closet?

Your robot is lost in a deviously complex maze, and requires your help to identify where it is!  This week's lab is similar to last week's: using distance sensor data, you will identify your robot's position.  However, rather than being in one of two rooms, your robot can now be in any of 9 spots in the maze, and facing any of 4 directions (north, west, south, or east), for a total of $9\times 4=36$ total possible states to discriminate between!

<raw>
<canvas class="illustration" id="maze" style="height:400px"></canvas>
<p class="caption">The robot maze, which will stay constant throughout the class.  The robot is collecting a measurement at position 4 and angle 90 (east).</p>
<script>
make_maze("maze", [{pos:4, angle:90, color:'blue'}]);
</script>
</raw>

In addition, this week we will allow rotating the distance sensor to get more measurements at different angles.  We can do that using the following syntax in Jupyter on the robots:

```
>>> bot.setTurret(45) # angle between -90 and 90, 0 is straight
None
>>> bot.getDistance() # read from sensor in centimeters
32.12
```

We also provide an API for calculating the expected sensor reading for a position in the maze, so you don't have to hardcode distances for each state like in last week's lab.  We can encode a possible state of the robot as a position $p$ (an integer between $0$ and $8$, see diagram) and an angle $a$ in degrees (going clockwise with $0^\circ$ pointing up).  Using this representation, we can get the sensor reading we might expect a robot in the top left cell ($p=0$) with its sensor pointing down ($a=180$) to measure:

```
>>> gm.simulatedDistance(0, 180)
TODO: insert real value here
```

Building off of your implementation from last week's lab, write code in the bottom of the lab two Jupyter notebook to compute the probability of being in each possible state (position and orientation pair) after collecting some sensor readings.  Then,

1. Calculate the likely state (position and orientation pair).
2. Calculate the most likely position for your robot.
3. Calculate the most likely orientation for your robot.

Discuss with your group the differences between each of these tasks, and ways you could accomplish them.  Is the most likely state the same as the most likely position and orientation?

## Formalizing decision making


### Cost Minimization and Hypothesis Testing
In the real world, we make decisions based off of series of observations. For example, I might have three hypotheses about the weather right now: sunny, rainy or snowy. I can decide pretty quickly based off of one observation of going outside or even looking out the window. In the probability theory framework, we encode possible scenarios as a set of hypotheses
$$
\mathcal{H} = \{H_0, H_1,...,H_n\}
$$
where $n$ is the number of hypotheses under consideration. First, we'll consider binary hypothesis testing, in which we are choosing between just two hypotheses 
$$
\mathcal{H} = \{H_0, H_1\}
$$

Our general framework for decision making will be one of cost-minimization. I can assign cost function (which will depend on the problem context) and aim to make decision rules such that I can minimize my cost. We denote $C_{ij} = \tilde{C}(H_i, H_j)$ to be the cost of deciding that the correct hypothesis is $H_i$ when the true hypothesis is $H_j$. 

<block Notation note>
A cost function is just a function that maps some event to a cost, or price that we pay. For example, a cost function in the real world is that I lose 5% of my grade for every homework assignment I don't do. 
</block>

- Let's say that I'm trying to figure out without looking if an m&m is green ($\mathcal{H}_0$) or red ($\mathcal{H}_1$). There's not really any consequence if my decision is wrong, so a reasonable cost function is 

$$
C_{00} = C_{11} = 0 \\
C_{01} = C_{10} = 1
$$

- But on the other hand, say I'm trying to determine if a patient is healthy ($\mathcal{H}_0$) or has cancer ($\mathcal{H}_1$). Then, our cost is no longer symmetric; it's much worse to decide that they are healthy when they have cancer than to decide that they have cancer when they are healthy (although neither is great). So a reasonable cost function might look like 

$$
\begin{aligned}
C_{00} = C_{11} &= 0 \\
C_{10} &= 1000 \\
C_{01} &= 10
\end{aligned}
$$

### Decision Rules 

We'll denote the hypothesis we choose as $\hat{H}$ and the true hypothesis as $H$. We want to choose $\hat{H}$ to minimize expected cost:

$$
\hat{H}(\cdot) = \arg\min_{f(\cdot)} \mathbb{E}[\tilde{C}(f(y), H)]
$$
Here, the $\mathbb{E}$ stands for expectation- and we'll generally just think of that as what cost we would receive "on average".

<block Notation note>
The $\arg \min$ of a function $f(x)$ is the value (or set of values) $x$ that results in the minimum value of $f(x)$. For example, $\arg\min x^2$ is $x=0$. Identically, the $\arg \max$ of a function $f(x)$ is the value (or set of values) $x$ that results in the maximum value of $f(x)$. For example, $\arg\max -x^2$ is $x=0$. 
</block>

where $f$ is the space of all functions that map observations to a hypothesis conclusion. In words, we're just looking for the function that maps observations $y$ to hypotheses $H_0, H_1$ that minimizes the expected cost we'll receive. 

<block Notation note>
Don't worry too much about expectation notation, but if you're curious, the expected value of a random variable $X$ with pmf $p_X$ is computed as 

$$
\mathbb{E}[X] = \sum_x xp_X(x)
$$
</block>

Now, given a specific observation point $y_0$, if we choose $\hat{H}(y_0) = H_0$ then expected cost is 

$$
C_{00}p_{H|y}(H_0|y_0) + C_{01}p_{H|y}(H_1|y_0)
$$

Similarly, if we choose $\hat{H}(y_0) = H_1$ then expected cost is 

$$
C_{10}p_{H|y}(H_0|y_0) + C_{11}p_{H|y}(H_1|y_0)
$$

So we see that the hypothesis we choose is just the hypothesis that results in a lower expected cost: we choose $H_1$ when 
$$
p_{H|y}(H_1|y_0)(C_{01} - C_{11}) > p_{H|y}(H_0|y_0)(C_{10} - C_{00})
$$

and $H_0$ otherwise. 

### Exercise: 

Using Bayes rule, rewrite this decision rule in terms of the measurement densities, i.e. using $p_{y|H}(\cdot)$ rather than $p_{H|y}(\cdot)$ as we have done above. Use that the probability $H_0$ is the ground truth is $P_0$, and the probability $H_1$ is the ground truth is $P_1$. 

<solution>
We can rewrite our original form as 

$$
L(y)=\frac{p_{H|y}(H_1|y)}{p_{H|y}(H_0|y)}\underset{H_0}{\overset{H_1}{\gtreqless}} \frac{(C_{10}-C_{00})}{(C_{01}-C_{11})}=\eta
$$

Now, multiplying both sides by $\frac{P_0}{P_1}$, we get 

$$L(y)=\frac{p_{y|H}(y|H_1)}{p_{y|H}(y|H_0)}\underset{H_0}{\overset{H_1}{\gtreqless}} \frac{P_0(C_{10}-C_{00})}{P_1(C_{01}-C_{11})}=\eta.$$

This is called the Likelihood Ratio Test.
</solution>

Looking at the form of the Likelihood Ratio test, 

$$
L(y)=\frac{p_{y|H}(y|H_1)}{p_{y|H}(y|H_0)}\underset{H_0}{\overset{H_1}{\gtreqless}} \frac{P_0(C_{10}-C_{00})}{P_1(C_{01}-C_{11})}=\eta.
$$

It is interesting to note that we don't actually require the observations $y$ themselves to make the decision- it suffices to know the likelihood ratio $L(y)$. We call quantities like $L(y)$ sufficient statistics, because they contain all the information that we require to make decisions. 

### Frameworks for Decision Making

One way in which we could try to make decisions is by trying to minimize our probability of error. This corresponds to using the symmetric 0/1 cost function we introduced above: 
$$
C_{00} = C_{11} = 0 \\
C_{01} = C_{10} = 1
$$

Substituting these cost functions into the generalized decision rule we created above, we see that this corresponds to choosing 
$$
\hat{H}(y) = \arg \max_{H \in \{H_0, H_1\}} p_{H|Y}(H|y)
$$

This rule is known as the Maximum A Posteriori (MAP) decision rule. In the special case where the two hypotheses are equally likely, we can substitute $P_0 = P_1 = \frac{1}{2}$ into the form of the Likelihood Ratio Test you derived in the exercise above, which results in the decision rule known as the Maximimum Likelihood decision rule: 

$$
\hat{H}(y) = \arg \max_{H \in \{H_0, H_1\}} p_{y|H}(y|H)
$$

