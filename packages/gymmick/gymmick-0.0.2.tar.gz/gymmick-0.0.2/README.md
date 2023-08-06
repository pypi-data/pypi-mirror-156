# Gymmick

A library offering simple functionality for the creation of simple visuals-based OpenAI Gym environments.

## Description

The purpose of this library is to create an easier way for users to make custom visual-based environments compatible with OpenAI Gym. Along with the basics of any Gym environment (ENV class and defining functions), the library will contain special functions to make
state handling (for observation creation) easier as well as a predefined visualization tool which can be activated upon request 
(by changing a dedault argument when creating an environment instance). If the user does not want a visual/physics-based environment, 
they can opt to add their own variables to an optional argument dictionary when instantiating the class and have complete freedom
with the manipulation of the values in said dictionary as the states of the environment change.

This library is not an advanced tool, but provides users freedom to do (almost) whatever they want in their environment. Flexibility for some environment functions is a priority and pending features include:

 - `Functions for Collision Detection`
 - `Gravity for Members of the Environment`
 - `Support for Grid-Based Environments`
 - `Visibility and "Tangibility" of Environment Members`

## Installation

To install, simply use the command:
```python
pip install gymmick
```

## Usage

Import:

```python
from gymmick import CustomEnv
from gymmick import Circle, Rect
```

Create Environment Instance:

```python
# The action_handler method is responsible for controlling how the state changes in response to an action as well as
# ... what kind of observations are returned back to the environment given the parameters: action, environment members, env episode 
# ... length and any other user-configured variables
def action_handler(action, members, length, other):
    other['state'][0] += action -1 
    length[0]-=1
    if other['state'][0] >=37 and other['state'][0] <=39: 
        reward = 1 
    else: 
        reward = -1 
    if length[0] <= 0: 
        done = True
    else:
        done = False
    info = {}
    return other['state'][0], reward, done, info

# The CustomEnv class is initialized with the action space, observation space, episode length, action handler, and any other 
# ... user-configured variables
env = gymmick.CustomEnv(spaces.Discrete(3), spaces.Box(low = np.array([0]), high = np.array([100])), 60, action_handler, state = 38+random.randint(-3, 3))
```

An environment member (either ```Circle``` or ```Rect```) can be instantiated using:

```python
new_circle = gymmick.Circle(x, y, r, vx, vy, m, color)

new_rect = gymmick.Rect(x, y, w, h, vx, vy, m, color)
```

And added to your environment using:

```python
env.add_member(new_circle)
env.add_member(new_rect)
```