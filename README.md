# BioLogic

## Overture 🔋 

Ever wanted to programatically control your potentiostat? You've come to the right place, for this library contains functionality for interfacing with potentiostats from [BioLogic](https://www.biologic.net/).

## Acknowledgement

This library is in part built upon previous work and advice by vores danske venner hos DTU: [PyExpLabSys](https://github.com/CINF/PyExpLabSys). It also borrows from the OEM's official examples. Lastly, the containerization couldn't have happened without [pywine](https://github.com/webcomics/pywine). So, big thanks to [Kenneth Nielsen](https://github.com/KennethNielsen) and [Tobix](https://github.com/TobiX)!

## Motivation

Potentiostats from our comrades across the pond at BioLogic are second to none. Their GUI—[EC-Lab](https://www.biologic.net/support-software/ec-lab-software/)—is also great, but is at the end of the day bound by the limitations of a GUI.

There are three main reasons for preferring programmatic control over a GUI:

### 1. Data Automation

We cycle a lot of cells. Like, a lot. As such, we have a lot of data. Time is a valuable commodity and we'd rather spend our time gaining insights from our experiments, rather than spending it manually uploading to our server ([drops](https://github.com/dansteingart/drops)).

Sometimes the OEM doesn't provide an SDK/API, in which case we must resort to scrapers. BioLogic _does_ provide one. They even provide a suite of minimal examples in their [excellent documentation](https://www.biologic.net/support-software/ec-lab-oem-development-package/) to get one started.

### 2. Syncing Instruments

Oftentimes in our experiments we want to do something in tandem with cell cycling, e.g. [acoustics](https://github.com/steingartlab/acoustics_hardware), control temperature or apply variable stack pressure. Then it becomes very useful—almost necessary—to be able to programatically control these different systems in one place (e.g. proftron Dan's [pithy](https://github.com/dansteingart/pithy)) to have one event trigger another.

This is probably best illustrated with an example.

Let's say we're running a experiment where we do high-frequency acoustics for the first minute of each charge step of each cycle. Lining up the acoustics with the cycling down to seconds, or even sub-seconds, would be intractable without a real-time data stream. Even if we'd calculate precisely when the next step would start, we still might be off by several minutes. Batteries are stochastic little buggers.

### 3. Simplicity

A couple of thousand lines of code might at first glance seem like just an added layer of complexity. In reality it's everything but that. Having this functionality allows one to input parameters and start experiment in a single script, helping one to maintain oversight. KISS.

## Technical Details

This library _can_ be run as a standalone application but is actually optimized to be run containerized.

This only runs on Windows. I know, I know. It's just a design choice by BioLogic. Nothing is perfect. _TODO: There is a way around that though, albeit a little hacky. To be able to run it as a standalone container it is run as a [Wine](https://www.winehq.org/) compatibility layer._


It uses the `http` protocol to receive commands (simple, robust, little overhead) and `mqtt` to submit relay data (great when cache-ing is needed).


## Example

```
import requests 

ip = '0.0.0.0'
port = '5001'

params = {
    'exp_id': 'test/test',
    'technique': 'OCV',
    'params': {
            'duration': {
                    'ecc': 'Rest_time_T',
                    'value': 3.0,
                    'index': 0
        },
            'record_dt': {
                    'ecc': 'Record_every_dT',
                    'value': 1.0,
                    'index': 0
        },
            'E_range': {
                    'ecc': 'E_Range',
                    'value': 5,
                    'index': 0
        }
    }
}

response = requests.post(f'http://{ip}:{port}/run', timeout=3, json=params)

```

### Disclaimer

This library was written with a narrow scope: Run CC/CV/EIS on HCP-1005 and SP-150 Biologics remotely and programmatically through [pithy](https://github.com/dansteingart/drops), dumping data to [drops](https://github.com/dansteingart/drops). It is of course written with modularity in mind but in the spirit of the MIT License we assume no reliability.

We are, after all, battery scientists, not software engineers.

---

Nitty gritty details [here](https://www.notion.so/ceecnyc/BioLogic-Programmatic-Control-b380082a3afd44e4b1ea3e22fede9d11#b0960bc5f0f344bb90784f707e637745) (internal).
