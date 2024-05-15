# ClassTranscribe Flash Detection Documentation


<!-- Contents -->
## Components
1. **Flash Definition**
    * General Flash
    * Red Flash

2. **What makes a flash dangerous?**
    * Flash Rate
    * Flash Screen Coverage
    * User Preferences

3. **Other assumptions** 
    * Viewing Distance
    * Screen Size
    * Does the Device Matter?

4. **Implementation Details**
    * Sliding window
    * State machine for red flash detection





##
<!-- Short explanations and source(s) -->
## Flash Definition
According to [WCAG Success Criterion 2.3.1](https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html#dfn-flash"), flash is a pair of opposing changes in relative luminance that can cause seizures in some people if it is large enough and in the right frequency range.

### General Flash
* **General flash:** Defined as a pair of opposing changes in *relative luminance* of at least 0.1 where the *relative luminance* of the darker image is below 0.80
    * "a pair of opposing changes" is defined as an increase followed by a decrease, or a decrease followed by an increase
* **Relative luminance:** the relative brightness of any point in a colorspace, normalized to 0 for darkest black and 1 for lightest white


### Red Flash
* **Red flash:** defined in [WCAG Success Criterion 2.3.1](https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html) as any pair of opposing transitions involving a saturated red and the chromaticity difference of those two frames is sufficiently high (see below).
* **Red transition:** A transition into or out of a state with a significant portion of redness (we refer to this as the red percentage) OR a transition between two states with a large enough *chromaticity difference*.
* **Red percentage:** Formally defined by [WCAG Success Criterion 2.3.1](https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html) as $$R_{percent} = \frac{R}{R + G + B} \times 100\%$$
    * Any pixel or frame with $R_{percent}\ge80\%$ has a "significant portion of redness" 
* **Chromaticity difference:** The [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) between the *chromaticity coordinates* of two pixels. $$C_{diff}=\sqrt{(u_1 - u_2)^2 + (v_1 - v_2)^2 }$$
    * In a dangerous red flash, $C_{diff} > 0.2$ 
* **Chromaticity coordinates:** A position within the [CIELUV color space](https://en.wikipedia.org/wiki/CIELUV). Represented as an ordered pair $(u,v)$.
<div style="display:flex;justify-content:center;">
    <img src="https://i.imgur.com/v7oLwkD.png" alt="drawing" style="width:400px;"/>
</div>
* In the [WCAG Success Criterion 2.3.1](https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html), [CIELUV coordinates](https://en.wikipedia.org/wiki/CIELUV) (chromaticity coordinates) are calculated using [CIE XYZ](https://en.wikipedia.org/wiki/CIE_1931_color_space) coordinates, represented by $(x,y,z)$. These are then calculated from normalized RGB pixel values:
    * Chromaticity coordinates from CIE XYZ coordinates: 
        * $u = \frac{4x}{x + 15y + 3z}$, $v = \frac{9y}{x + 15y + 3z}$
    * CIE XYZ coordinates from pixel RGB values:
        * $x = 0.4124564 \times R + 0.3575761 \times G + 0.1804375 \times B$
        * $y = 0.2126729 \times R + 0.7151522 \times G + 0.0721750 \times B$
        * $z = 0.0193339 \times R + 0.1191920 \times G + 0.9503041 \times B$
    * Note that the RGB color values are normalized (in the range `[0.0,1.0]`)




##
## What makes a flash dangerous?
A single isolated flash is not dangerous, but what is? We consulted the WCAG 2.2 guidelines to find out how often flashing needs to occur and what portion of the screen must be flashing to be considered dangerous.

### Flash Rate
According to the [WCAG Success Criterion 2.3.1](https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html) web sites should not have more than 3 flashes in a one-second window.
### Flash Screen Coverage
In the trivial case for dangerous screen flashing, we may see the entire screen change from dark to light. On the other hand, a single flashing pixel should not be considered dangerous. 

We consulted the [WCAG 2.2 guidelines](https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html) on flashing to determine what portion of the screen must be flashing to be considered dangerous. According to these guidelines *the combined area of flashes occurring concurrently occupies no more than 25% of any 10 degree visual field on the screen at typical viewing distance*.

While there are references to exact pixel region sizes, these are quite outdated. Additionally, using the 10 degree visual field calculation more closely matches newer techniques (not yet standardized) using [CSS pixels](https://www.w3.org/TR/WCAG21/#dfn-css-pixels). (also known as [reference pixels](https://www.w3.org/TR/css-values-3/#reference-pixel))
### User Preferences
The condition of the dangerous flash may vary according on the user's preferences. Representative instances include playback speed, zoom, and color inversion / colorblind modes.
* **Playback Speed**:
    * A user could be watching a video at 2x speed. In this case, we lengthen the sliding window (see implementation details) to detect if this change creates new dangerous flashing.
* **Zoom in/out**:
    * A user could zoom in or out on various regions of the video that may contain flashing. In this case, we adjust the effective viewing distance to create finer flash detection regions. (see implementation details)
* **Color Inversion / Colorblind Modes**:
    * Color adjustment could create new regions of dangerous flashing, which is difficult to predict. Currently, we do no checks for these settings and opt to warn the user when switching on these modes.


### Viewing Distance
* With screen size held constant, a flash becomes less dangerous when viewed at longer distances and more so at shorter distances. 
* **Assumptions**
    * The average viewing distance for desktop is 24.8" (63 cm) ([Wolfgang 2002](https://journals.lww.com/optvissci/Abstract/2002/03000/The_Proximity_Fixation_Disparity_Curve_and_the.10.aspx)).
    * The average viewing distance for smartphones is 11.5" (29.2 cm) ([Long et al. 2017](https://pubmed.ncbi.nlm.nih.gov/27716998/)).


### Screen Size
* With viewing distance held constant, a flash becomes less dangerous when viewed with a smaller screen and more so with a larger screen. 
* **Assumptions**
    * The average laptop screen size is 14" (35.6 cm) ([Erlita et al. 2023](https://doi.org/10.22219/sm.Vol19.SMUMM1.22564))
    * The average smartphone screen size is 6.4" (16.3 cm) ([Erlita et al. 2023](https://doi.org/10.22219/sm.Vol19.SMUMM1.22564))

### Does the Device Matter?

If the flash covers some portion of a computer or smartphone screen, screen size and viewing distance nearly cancel each other out. This is largely due to the fact that people tend to view smaller screens from a shorter distance and larger screens from a farther distance. In practice, we can simply use one calculation based on the average device rather than recalculating the detection sensitivity based on various device types and screen sizes.


##
## Implementation Details
### Sliding Window
To detect frames with the flash, we use [sliding window](https://www.geeksforgeeks.org/window-sliding-technique/) technque. At normal playback speed, we check a rolling 1-second window and count the number of flashes. If this count is at least 3, then we mark this area as dangerous.

### State Machine for Red Flash Detection
Per WCAG's [Red Flash Definition](###Red-Flash), there are two components to a red flash, the **red percentage** and **chromaticity difference**. We developed a state machine to determine when a red flash is dangerous. Note that currently, our program marks areas having one red flash as dangerous.

![Screenshot 2024-03-20 at 1.42.37 PM](https://hackmd.io/_uploads/rkPS0sO06.png)

Note:
* `SR = Saturated Red Present` (one frame with $R_{percent} \ge 0.8$)
* `CC = Large Chromaticity Change/Difference` ($C_{diff} \gt 0.2$) 
* **`E`** is the flash state; when we reach this state, we determine that a dangerous red flash is present.

#### Set of states
We begin by segmenting each frame into a specified number of regions. Each of these regions maintains a *set* of states. Each state in this set has an associated letter (A, B, C, D, or E), along with an associated starting index (e.g., 0). For example, the set of states for a region could be $\{[D, 0], [A, 1], [D, 2]\}$. Note that, as in this example, some of the states corresponding to a particular region may have the same letter.

#### How do we progress in the state machine?
We first determine the chromaticity and saturated red percentage for the region. When we see a new frame, we can add a new state to the state machines corresponding to each region. If the region $i$ has a saturated red, then we can add the state $\{B, i\}$ to that region's state machine. Else, we can add the state $\{A, i\}$.

We can also determine whether we can progress our pre-existing states in each region's state machine. For example, suppose that our set of states for some region is $\{[A, 0]\}$. At index 1, suppose the region does not have a saturated red, and there is a change in chromaticity less than $0.2$. Then we would have $\{[A, 0], [A, 1]\}$. Now, suppose that at index 2, the region has a saturated red. Also, assume that the region's chromaticity difference between index 2 and index 0 is $> 0.2$, while its chromaticity difference between index 2 and index 1 is $\leq 0.2$. Given this, our new set of states would be $\{[C, 0], [A, 1], [A, 2]\}$. In this example, we were able to add a new state, $[A, 2]$. Additionally, having seen both a saturated red and a chromaticity change that is $> 0.2$, we were able to transition from state $[A, 0]$ to state $[C, 0]$.

#### How do we remove states from the state machine?

States have an associated index because we are only intested in determining whether a red flash occurs within a one-second window of time. So let $i$ be the initial starting index of this one-second window, and let $j$ be the initial ending index. As we add a frame, our window of interest will now start at $i + 1$ and end at $j + 1$. Thus, we can safely remove states having index $i$ from the set of states; they haven't reached the flash state "E" within a one-second window, so they don't constitute a red flash.

Currently, we also remove states for a particular index having a lower "quality" than another state for that index. That is, if our state set is $\{[A, 0], [C, 0]\}$, then we will remove $[A, 0]$ because it is further from the flash state. However, this may mean that we miss detecting a red flash in some rare cases.

#### How do we detect a red flash?

After we add a frame, we check the state machines associated with each region to see if any have a state with letter "E". If so, there is a red flash in that region, and the red flash begins at the index associated with the state. Using the frame rate, we can determine the timestamp at which the red flash occurred.

#### How do we determine the chromaticity difference?

We save all of the $(u, v)$ chromaticity values we have for a given state. Then, when we see a new frame, we determine the difference between the region's current chromaticity and all of the saved values. If this difference is $> 0.2$, then we can take a $CC$ transition in the state machine.

<!-- \begin{tikzpicture}[scale=0.2]
\tikzstyle{every node}+=[inner sep=0pt]
\draw [black] (5.5,-26.4) circle (3);
\draw [black] (14.5,-33.2) circle (3);
\draw (14.5,-33.2) node {$B$};
\draw [black] (14.5,-19.7) circle (3);
\draw (14.5,-19.7) node {$A$};
\draw [black] (28,-26.4) circle (3);
\draw (28,-26.4) node {$C$};
\draw [black] (28,-9) circle (3);
\draw (28,-9) node {$D$};
\draw [black] (44.2,-26.4) circle (3);
\draw (44.2,-26.4) node {$E$};
\draw [black] (44.2,-26.4) circle (2.4);
\draw [black] (0.3,-26.4) -- (2.5,-26.4);
\fill [black] (2.5,-26.4) -- (1.7,-25.9) -- (1.7,-26.9);
\draw [black] (7.89,-28.21) -- (12.11,-31.39);
\fill [black] (12.11,-31.39) -- (11.77,-30.51) -- (11.17,-31.31);
\draw (8.27,-30.3) node [below] {$SR$};
\draw [black] (7.91,-24.61) -- (12.09,-21.49);
\fill [black] (12.09,-21.49) -- (11.15,-21.57) -- (11.75,-22.37);
\draw [black] (17.18,-31.85) -- (25.32,-27.75);
\fill [black] (25.32,-27.75) -- (24.38,-27.66) -- (24.83,-28.56);
\draw (23.07,-30.31) node [below] {$CC$};
\draw [black] (31,-26.4) -- (41.2,-26.4);
\fill [black] (41.2,-26.4) -- (40.4,-25.9) -- (40.4,-26.9);
\draw (36.1,-26.9) node [below] {$CC$};
\draw [black] (17.19,-21.03) -- (25.31,-25.07);
\fill [black] (25.31,-25.07) -- (24.82,-24.26) -- (24.37,-25.16);
\draw (26.2,-22.53) node [above] {$CC\mbox{ }and\mbox{ }SR$};
\draw [black] (16.85,-17.84) -- (25.65,-10.86);
\fill [black] (25.65,-10.86) -- (24.71,-10.97) -- (25.33,-11.75);
\draw (19.41,-13.85) node [above] {$CC$};
\draw [black] (30.04,-11.2) -- (42.16,-24.2);
\fill [black] (42.16,-24.2) -- (41.98,-23.28) -- (41.24,-23.96);
\draw (36.63,-16.24) node [right] {$CC\mbox{ }and\mbox{ }SR$};
\end{tikzpicture} -->


