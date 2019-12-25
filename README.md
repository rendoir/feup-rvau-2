# feup-rvau-2

## Installation

Install Python 3 and, optionally, virtualenv

Clone the repository
```bash
git clone https://github.com/rendoir/feup-rvau-2.git
```
If using a Python3 virtualenv, start and activate it with:
```bash
cd feup-rvau-2/src/
virtualenv -p python3 env
. env/bin/activate
```
Install Python dependencies via:
```bash
pip3 install -r ../dependencies.txt
```

## Running

### Offside Line with Manual Homography

Run the manual homography offside line Python3 script using:
```bash
python3 offside.py
```

This script is prepared to handle any image from the right side of the field, with all penalty area points visible.  
Click on the 4 points of the penalty area in a clockwise fashion<sup>1</sup>. Press Enter.  
Click on the player where you'd want to draw the line. Press Enter.   

<sup>1</sup> Some machines only work with counter-clockwise (mainly when running Windows)


### Free-kick with Manual Homography

Run the manual homography free-kick Python3 script using:
```bash
python3 free_kick.py
```

This script is prepared to handle any image from the left side of the field, with all goal area points visible.  
Click on the 4 points of the goal area in a clockwise fashion<sup>1</sup>. Press Enter.  
Click on the ball. Press Enter.   

<sup>1</sup> Some machines only work with counter-clockwise (mainly when running Windows)


### Offside Line with Automatic Homography

Run the automatic homography offside line Python3 script using:
```bash
python3 offside_automatic.py
```

This script should be able to handle any image from the right side of the field, with all penalty area points visible. However, this isn't guaranteed as per image parameter tunning is often needed for lines and field detection.  
Click on the player where you'd want to draw the line. Press Enter.   


### Free-kick with Automatic Homography

Run the automatic homography free-kick Python3 script using:
```bash
python3 free_kick_automatic.py
```

This script should be able to handle any image from the left side of the field, with all goal area points visible. However, this isn't guaranteed as per image parameter tunning is often needed for lines and field detection.  
Click on the ball. Press Enter.   
