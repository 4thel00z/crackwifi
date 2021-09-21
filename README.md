# crackwifi

![crackwifi.png](https://raw.githubusercontent.com/4thel00z/logos/master/crackwifi.png)

## Motivation

I am stupid hägger and do not want to have to remember reaver specific commands to hack noobs.

## Installation

```shell
pip install crackwifi
```

## Usage

```python
from crackwifi import dump_networks, monitor

if __name__ == '__main__':
    with monitor("wlx6cfdb9b29a25"):
        networks = dump_networks(10)
	first = list(networks.values())[0]
	for progress in first.attack():
		print(progress)
```

## License

This project is licensed under the GPL-3 license.
