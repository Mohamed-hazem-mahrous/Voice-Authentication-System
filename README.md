# Voice Authentication System

## Table of Contents

- [Introduction](#introduction)
- [Team Members](#Team-Members)
- [Features](#features)
- [Picture Overview](#Picture-Overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Introduction
This Python desktop application utilizes voice fingerprint and spectrogram technology to identify individuals based on their unique vocal characteristics. The system can be trained on up to 8 individuals and operates in two distinct modes to ensure secure access.

## Team Members
The following team members have contributed to this project:
- Mohamed Hazem Yehya
- Assem Hussein
- Kyrolos Emad
- Arsany Maged


## Features
The Voice Authentication System app have 2 modes:
1. **Mode 1 – Security Voice Code:** Access is granted only if the user speaks a specific pass-code sentence.

2. **Mode 2 – Security Voice Fingerprint:** Access is granted to specific individuals who say the valid pass-code sentence.

## Picture Overview
[Picture Overview](https://github.com/Mohamed-hazem-mahrous/Voice-Authentication-System/assets/94749599/16ac3774-f785-426c-9abe-2ebd62328fa8)

## Requirements
List the dependencies and requirements needed to run the application.
- PyQt5
- pyqtgraph
- librosa
- numpy
- pyaudio
- wave
- pandas
- glob
- scipy
- sklearn
- fastdtw

## Installation

Install the required dependencies using pip

```bash
pip install PyQt5 pyqtgraph librosa numpy pyaudio pandas scipy scikit-learn fastdtw
```


## Usage
Run the recorder first to record the users voices:
```bash
python recorder.py
```

Run the hashing file after recording to hash the sound:
```bash
python Hashing.py
```

Run main.py after that to test the Accessibility:
```bash
python main.py
```


## Contributing
Contributions to Voice Authentication System
 are welcome! If you encounter any issues or have suggestions for improvements, please create a new issue or submit a pull request.

When contributing, please ensure that you follow the existing coding style and include clear commit messages to maintain a well-documented project history.

